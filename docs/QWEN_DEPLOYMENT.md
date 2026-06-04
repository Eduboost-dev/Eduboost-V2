# Qwen 2.5 Coder 14B on Azure GPU VM - Deployment Guide

This guide explains how to deploy and run **Qwen 2.5 Coder 14B** on an Azure VM with NVIDIA GPU support.

## Overview

Qwen 2.5 Coder 14B is a high-performance coding model with 14 billion parameters. The infrastructure includes:
- **Bicep Template**: `bicep/qwen_gpu_vm.bicep` - Azure infrastructure as code
- **Setup Script**: `scripts/setup_qwen_gpu_vm.sh` - Automated VM configuration
- **Parameters File**: `bicep/qwen_gpu_vm.parameters.json` - Deployment configuration

## Hardware Requirements

The template supports multiple Azure GPU VM SKUs:

| SKU | vCPU | RAM | GPU | VRAM | Approx Cost/hr |
|-----|------|-----|-----|------|---|
| Standard_NC4as_T4_v3 | 4 | 28GB | 1x T4 | 16GB | $0.35 |
| Standard_NC8as_T4_v3 | 8 | 56GB | 2x T4 | 32GB | $0.70 |
| Standard_NC6s_v3 | 6 | 112GB | 1x V100 | 32GB | $0.90 |

**Recommendation**: Start with `Standard_NC4as_T4_v3` - sufficient for 14B model with 4-bit quantization.

## Prerequisites

1. **Azure Subscription** with quota for GPU VMs
2. **Resource Group** created in Azure
3. **SSH Key Pair** for authentication
4. **Azure CLI** installed locally

### Generate SSH Key (if needed)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/azure_qwen -C "qwen-vm"
cat ~/.ssh/azure_qwen.pub  # Copy this for parameters
```

## Deployment Steps

### Step 1: Prepare Parameters

Edit `bicep/qwen_gpu_vm.parameters.json`:

```json
{
  "parameters": {
    "location": {
      "value": "eastus"  // Change to your region
    },
    "vmName": {
      "value": "qwen-coder-14b"
    },
    "adminUsername": {
      "value": "eduboost"
    },
    "adminPublicKey": {
      "value": "ssh-ed25519 AAAA... your-key-here"  // Paste your public key
    },
    "vmSize": {
      "value": "Standard_NC4as_T4_v3"
    },
    "dataDiskSizeGB": {
      "value": 256  // For model storage
    }
  }
}
```

### Step 2: Deploy with Azure CLI

```bash
# Set subscription
az account set --subscription <SUBSCRIPTION_ID>

# Create resource group (if needed)
az group create --name qwen-rg --location eastus

# Deploy
az deployment group create \
  --resource-group qwen-rg \
  --template-file bicep/qwen_gpu_vm.bicep \
  --parameters @bicep/qwen_gpu_vm.parameters.json
```

### Step 3: Get VM Details

```bash
# Get public IP
az vm show --resource-group qwen-rg --name qwen-coder-14b \
  --show-details --query publicIps -o tsv

# SSH into VM
ssh -i ~/.ssh/azure_qwen eduboost@<PUBLIC_IP>
```

### Step 4: Monitor Setup Progress

On the VM, check setup progress:

```bash
# View setup log
tail -f /var/log/qwen-setup.log

# Check GPU status
nvidia-smi
lsblk  # Check disk mounting
```

The setup script will run automatically via Custom Script Extension. This may take 10-20 minutes.

## Using Qwen 2.5 Coder 14B

Once setup completes, you have two options for inference:

### Option A: Ollama (Simpler, Recommended)

Ollama provides an easy-to-use API for model inference with automatic quantization.

**Start the service:**
```bash
sudo systemctl start ollama
sudo systemctl status ollama
```

**Pull the model (first time only, ~15-30 min):**
```bash
ollama pull qwen2.5-coder:14b
```

**Test the API:**
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder:14b",
    "prompt": "def fibonacci(n):",
    "stream": false
  }'
```

**Enable persistence:**
```bash
sudo systemctl enable ollama
```

### Option B: vLLM (Higher Performance)

vLLM provides better throughput for batch requests and custom OpenAI-compatible endpoints.

**Download the model:**
```bash
source /opt/qwen-env/bin/activate
mkdir -p /mnt/models/qwen-2.5-coder-14b
huggingface-cli download Qwen/Qwen2.5-Coder-14B \
  --local-dir /mnt/models/qwen-2.5-coder-14b
```

**Start vLLM:**
```bash
sudo systemctl start vllm
sudo systemctl status vllm
```

**Test the API (OpenAI-compatible):**
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-2.5-coder-14b",
    "prompt": "def fibonacci(n):",
    "max_tokens": 200
  }'
```

## Accessing the API from EduBoost

### From Python (Using vLLM)

```python
import requests

def query_qwen(prompt: str, max_tokens: int = 512) -> str:
    response = requests.post(
        "http://<VM_PUBLIC_IP>:8000/v1/completions",
        json={
            "model": "qwen-2.5-coder-14b",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()["choices"][0]["text"]

# Example usage
code_snippet = query_qwen("Write a Python function to reverse a string")
print(code_snippet)
```

### Using Environment Variables

```bash
# On EduBoost API server
export QWEN_API_URL="http://<VM_PUBLIC_IP>:8000"
export QWEN_MODEL="qwen-2.5-coder-14b"
```

### From Docker/EduBoost Container

If running EduBoost in Docker, ensure network connectivity:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - QWEN_API_URL=http://host.docker.internal:8000  # For Docker Desktop
      # OR use Azure VM IP if deployed to cloud
      - QWEN_API_URL=http://<VM_PUBLIC_IP>:8000
```

## Monitoring and Maintenance

### Check GPU Usage
```bash
# Real-time monitoring
nvidia-smi
nvtop  # Interactive GPU monitor
```

### View Logs
```bash
# Ollama logs
journalctl -u ollama -n 50 -f

# vLLM logs
journalctl -u vllm -n 50 -f

# Setup logs
tail -f /var/log/qwen-setup.log
```

### Check Model Disk Usage
```bash
df -h /mnt/models
du -sh /mnt/models/*
```

### Restart Services
```bash
sudo systemctl restart ollama
# OR
sudo systemctl restart vllm
```

## Cost Optimization

### Auto-shutdown
To reduce costs, auto-shutdown idle VMs:

```bash
# Setup auto-shutdown via Azure CLI
az vm auto-shutdown \
  --resource-group qwen-rg \
  --name qwen-coder-14b \
  --time 1800  # 6 PM UTC
```

### Model Quantization
Qwen models support quantization:
- **4-bit**: ~3.5GB VRAM (4x reduction, minimal quality loss)
- **8-bit**: ~7GB VRAM (2x reduction)
- **FP16**: Full precision (14B model ~28GB VRAM)

Ollama handles quantization automatically.

## Troubleshooting

### GPU Not Detected
```bash
nvidia-smi
# If not found, check Custom Script Extension logs:
tail -f /var/log/waagent.log
```

### Data Disk Not Mounted
```bash
lsblk
mount | grep /mnt
# Manually mount:
sudo mount /dev/sdc1 /mnt/models
```

### Model Download Fails
```bash
# Check internet connectivity
curl https://huggingface.co

# Use alternative mirror:
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen2.5-Coder-14B
```

### Out of Memory (OOM)
- Reduce `max-model-len` in vLLM config
- Use 4-bit quantization
- Reduce batch size
- Upgrade to larger VM

### Network Timeout
```bash
# Increase timeout or add retry logic in client code
# For curl:
curl --max-time 300 http://localhost:8000/...
```

## Cleanup

### Delete the VM and resources
```bash
az group delete --name qwen-rg --yes
```

This will delete all resources including:
- VM
- Disk
- Network interfaces
- Virtual network
- Public IP

## Next Steps

1. **Integrate with EduBoost**: Update API client to call Qwen endpoints
2. **Fine-tuning**: Consider fine-tuning Qwen on EduBoost-specific coding tasks
3. **Multi-GPU**: Scale to multiple GPUs for higher throughput
4. **API Gateway**: Add authentication and rate limiting via Azure API Management

## Support & Documentation

- **Qwen Documentation**: https://github.com/QwenLM/Qwen2.5
- **Ollama**: https://github.com/ollama/ollama
- **vLLM**: https://docs.vllm.ai/
- **Azure GPU VMs**: https://docs.microsoft.com/en-us/azure/virtual-machines/nc-series

---

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Status**: Ready for Deployment
