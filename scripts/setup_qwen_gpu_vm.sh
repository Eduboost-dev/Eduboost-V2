#!/usr/bin/env bash
set -euo pipefail

# EduBoost — Qwen 2.5 Coder 14B GPU VM Setup
# Sets up NVIDIA drivers, CUDA, and Qwen inference server (ollama/vLLM)
# Run as root or with sudo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="/var/log/qwen-setup.log"
DATA_MOUNT_POINT="/mnt/models"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
  echo "[ERROR] $*" | tee -a "$LOG_FILE"
  exit 1
}

log "=========================================="
log "Qwen 2.5 Coder 14B GPU VM Setup Starting"
log "=========================================="

# Detect if running as root
if [[ $(id -u) -ne 0 ]]; then
  error "This script must be run as root or with sudo."
fi

# 1) System Updates
log "Step 1: Updating system packages..."
apt-get update
apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  ca-certificates \
  gnupg \
  lsb-release \
  wget \
  git \
  vim \
  tmux \
  htop \
  nvtop \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  python3-pip

log "System packages updated."

# 2) Mount data disk (if not already mounted)
log "Step 2: Setting up data disk..."
if ! mountpoint -q "$DATA_MOUNT_POINT"; then
  # Find the data disk
  DISK_DEVICE=$(lsblk -nd -o NAME,SIZE | grep -v sda | head -1 | awk '{print $1}')
  
  if [[ -n "$DISK_DEVICE" ]]; then
    log "Found data disk: /dev/$DISK_DEVICE"
    
    # Create partition if needed
    if ! sudo fdisk -l /dev/"$DISK_DEVICE" | grep -q "$DISK_DEVICE"1; then
      log "Creating partition on /dev/$DISK_DEVICE..."
      echo -e "n\np\n1\n\n\nw" | fdisk /dev/"$DISK_DEVICE" || true
      sleep 2
    fi
    
    # Format and mount
    if ! blkid /dev/"${DISK_DEVICE}"1 &>/dev/null; then
      log "Formatting /dev/${DISK_DEVICE}1..."
      mkfs.ext4 -F /dev/"${DISK_DEVICE}"1
    fi
    
    mkdir -p "$DATA_MOUNT_POINT"
    mount /dev/"${DISK_DEVICE}"1 "$DATA_MOUNT_POINT"
    chmod 777 "$DATA_MOUNT_POINT"
    
    # Add to fstab for persistence
    if ! grep -q "$DATA_MOUNT_POINT" /etc/fstab; then
      echo "/dev/${DISK_DEVICE}1 $DATA_MOUNT_POINT ext4 defaults,nofail 0 2" >> /etc/fstab
    fi
    
    log "Data disk mounted at $DATA_MOUNT_POINT"
  fi
fi

# 3) Install NVIDIA GPU drivers and CUDA
log "Step 3: Installing NVIDIA drivers and CUDA..."

# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add - || true
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  tee /etc/apt/sources.list.d/nvidia-docker.list >/dev/null

apt-get update

# Install NVIDIA drivers
apt-get install -y --no-install-recommends \
  ubuntu-drivers-common \
  nvidia-driver-550

# Install CUDA Toolkit (compatible with driver 550)
log "Installing CUDA Toolkit 12.4..."
apt-get install -y --no-install-recommends \
  nvidia-cuda-toolkit

log "NVIDIA drivers and CUDA installed."

# 4) Setup Python environment
log "Step 4: Setting up Python environment..."

# Create a venv for ML workloads
VENV_PATH="/opt/qwen-env"
if [[ ! -d "$VENV_PATH" ]]; then
  log "Creating Python venv at $VENV_PATH..."
  python3.11 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Upgrade pip
pip install --upgrade pip setuptools wheel

log "Python venv created at $VENV_PATH"

# 5) Install Ollama (easiest option for Qwen inference)
log "Step 5: Installing Ollama..."

OLLAMA_VERSION="0.1.26"
OLLAMA_URL="https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-linux-amd64.zip"

if ! command -v ollama &> /dev/null; then
  # Create ollama user
  if ! id -u ollama &>/dev/null; then
    useradd -r -s /bin/false -m -d /var/lib/ollama ollama
  fi
  
  mkdir -p /opt/ollama
  cd /opt/ollama
  
  log "Downloading Ollama v${OLLAMA_VERSION}..."
  wget -q "$OLLAMA_URL" -O ollama.zip
  unzip -q ollama.zip
  chmod +x ./ollama
  ln -sf /opt/ollama/ollama /usr/local/bin/ollama
  
  mkdir -p /var/lib/ollama
  chown -R ollama:ollama /var/lib/ollama
  
  log "Ollama installed."
else
  log "Ollama already installed."
fi

# 6) Create Ollama systemd service
log "Step 6: Creating Ollama systemd service..."

cat > /etc/systemd/system/ollama.service <<'EOF'
[Unit]
Description=Ollama LLM Server
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
User=ollama
Group=ollama
Type=simple
StandardOutput=journal
StandardError=journal

# GPU support
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="OLLAMA_MODELS=/mnt/models/ollama"

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /mnt/models/ollama
chown -R ollama:ollama /mnt/models/ollama

systemctl daemon-reload
systemctl enable ollama.service
log "Ollama service configured."

# 7) Install vLLM (alternative, higher performance option)
log "Step 7: Installing vLLM..."

source "$VENV_PATH/bin/activate"

pip install --no-cache-dir \
  vllm \
  torch \
  transformers \
  accelerate \
  peft

log "vLLM and dependencies installed."

# 8) Create vLLM systemd service
log "Step 8: Creating vLLM systemd service..."

cat > /etc/systemd/system/vllm.service <<'EOF'
[Unit]
Description=vLLM Qwen 2.5 Coder 14B Server
After=network-online.target

[Service]
ExecStart=/opt/qwen-env/bin/python -m vllm.entrypoints.openai.api_server \
  --model /mnt/models/qwen-2.5-coder-14b \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096 \
  --trust-remote-code
Restart=always
RestartSec=3
User=ollama
Group=ollama
Type=simple
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
log "vLLM service configured."

# 9) Setup startup script for model pulling
log "Step 9: Creating model initialization script..."

INIT_SCRIPT="/opt/init-qwen-models.sh"
cat > "$INIT_SCRIPT" <<'EOF'
#!/bin/bash
# Initialize Qwen models for Ollama

export OLLAMA_MODELS=/mnt/models/ollama

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Pulling Qwen 2.5 Coder 14B model..."
# Wait for ollama service to be ready
sleep 5

# Pull model (this will take time on first run)
/usr/local/bin/ollama pull qwen2.5-coder:14b 2>&1 | tee -a /var/log/ollama-init.log

if [[ $? -eq 0 ]]; then
  log "Model pull completed successfully."
else
  log "Model pull failed. Check /var/log/ollama-init.log"
fi
EOF

chmod +x "$INIT_SCRIPT"
log "Model initialization script created at $INIT_SCRIPT"

# 10) Create helper scripts
log "Step 10: Creating helper scripts..."

# Script to start Ollama with Qwen
cat > /usr/local/bin/start-qwen-ollama <<'EOF'
#!/bin/bash
export OLLAMA_MODELS=/mnt/models/ollama
/usr/local/bin/ollama serve
EOF
chmod +x /usr/local/bin/start-qwen-ollama

# Script to test Ollama API
cat > /usr/local/bin/test-qwen-api <<'EOF'
#!/bin/bash
echo "Testing Ollama API..."
curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:14b",
  "prompt": "Write a Python function to calculate fibonacci",
  "stream": false
}' | python3 -m json.tool
EOF
chmod +x /usr/local/bin/test-qwen-api

# Script to test vLLM API
cat > /usr/local/bin/test-qwen-vllm <<'EOF'
#!/bin/bash
echo "Testing vLLM API..."
curl -s http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-2.5-coder-14b",
    "prompt": "def fibonacci",
    "max_tokens": 100
  }' | python3 -m json.tool
EOF
chmod +x /usr/local/bin/test-qwen-vllm

log "Helper scripts created."

# 11) Print summary
log "=========================================="
log "Setup Complete!"
log "=========================================="

cat <<'SUMMARY'

### Qwen 2.5 Coder 14B GPU VM Setup Complete

**Services Configured:**
  1. Ollama (Primary inference server)
     - Port: 11434
     - Config: /etc/systemd/system/ollama.service
     - Models location: /mnt/models/ollama

  2. vLLM (Alternative high-performance server)
     - Port: 8000
     - Config: /etc/systemd/system/vllm.service
     - Model: /mnt/models/qwen-2.5-coder-14b

**Quick Start:**

1. Start Ollama service:
   sudo systemctl start ollama

2. Pull Qwen model (first run, ~15-30 min):
   ollama pull qwen2.5-coder:14b

3. Test Ollama:
   curl http://localhost:11434/api/generate -d '{"model":"qwen2.5-coder:14b","prompt":"Hello"}'

**Alternative: Using vLLM**

1. Create models directory:
   mkdir -p /mnt/models/qwen-2.5-coder-14b

2. Download model from Hugging Face:
   source /opt/qwen-env/bin/activate
   huggingface-cli download Qwen/Qwen2.5-Coder-14B --local-dir /mnt/models/qwen-2.5-coder-14b

3. Start vLLM:
   sudo systemctl start vllm

**GPU Status:**
   nvidia-smi
   nvtop (interactive GPU monitor)

**GPU Disk Free Space:**
   df -h /mnt/models

**Logs:**
   journalctl -u ollama -f    # Ollama logs
   journalctl -u vllm -f      # vLLM logs
   tail -f /var/log/qwen-setup.log

**Next Steps:**
  - Review /var/log/qwen-setup.log for any errors
  - Pull models: ollama pull qwen2.5-coder:14b
  - Test API endpoints
  - Integrate with your application

SUMMARY

log "Setup script completed. Check logs at $LOG_FILE"
