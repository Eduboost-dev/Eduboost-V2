# Qwen GPU VM - Quick Reference

## Deployment Commands

```bash
# 1. Set your public SSH key in parameters
nano bicep/qwen_gpu_vm.parameters.json

# 2. Deploy to Azure
az deployment group create \
  --resource-group qwen-rg \
  --template-file bicep/qwen_gpu_vm.bicep \
  --parameters @bicep/qwen_gpu_vm.parameters.json

# 3. Get IP address
az vm show --resource-group qwen-rg --name qwen-coder-14b \
  --show-details --query publicIps -o tsv

# 4. SSH into VM
ssh -i ~/.ssh/azure_qwen eduboost@<IP>
```

## On the VM - Quick Start

```bash
# Start Ollama
sudo systemctl start ollama

# Pull model (takes 15-30 min first time)
ollama pull qwen2.5-coder:14b

# Test it
curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:14b",
  "prompt": "def hello():",
  "stream": false
}'

# Enable auto-start
sudo systemctl enable ollama
```

## Monitoring

```bash
# GPU status
nvidia-smi

# Real-time GPU monitor
nvtop

# Disk usage
df -h /mnt/models

# Service logs (last 50 lines, follow)
journalctl -u ollama -n 50 -f

# Setup log
tail -f /var/log/qwen-setup.log
```

## API Endpoints

### Ollama (Port 11434)
```bash
# Generate response
curl -X POST http://<IP>:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder:14b",
    "prompt": "Write Python code to sort a list",
    "stream": false
  }'

# List models
curl http://<IP>:11434/api/tags

# Pull new model
curl -X POST http://<IP>:11434/api/pull -d '{"name": "qwen2.5-coder:14b"}'
```

### vLLM (Port 8000) - OpenAI Compatible
```bash
# Completions (chat-style)
curl -X POST http://<IP>:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-2.5-coder-14b",
    "prompt": "def fibonacci",
    "max_tokens": 512
  }'

# Chat API
curl -X POST http://<IP>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-2.5-coder-14b",
    "messages": [{"role": "user", "content": "Write Python code"}]
  }'
```

## Python Integration

```python
import requests
import json

def query_qwen_ollama(prompt: str) -> str:
    """Query Qwen via Ollama"""
    response = requests.post(
        "http://AZURE_VM_IP:11434/api/generate",
        json={"model": "qwen2.5-coder:14b", "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

def query_qwen_vllm(prompt: str) -> str:
    """Query Qwen via vLLM (OpenAI compatible)"""
    response = requests.post(
        "http://AZURE_VM_IP:8000/v1/completions",
        json={"model": "qwen-2.5-coder-14b", "prompt": prompt, "max_tokens": 512}
    )
    return response.json()["choices"][0]["text"]

# Test
result = query_qwen_ollama("print('hello world')")
print(result)
```

## Troubleshooting

```bash
# Check GPU
nvidia-smi -q
nvidia-smi -i 0 -q -d MEMORY

# Check service status
sudo systemctl status ollama
sudo systemctl status vllm

# Restart service
sudo systemctl restart ollama

# View custom script output
tail -f /var/lib/waagent/custom-script/download/0/stdout
tail -f /var/lib/waagent/custom-script/download/0/stderr

# SSH back in if connection drops
ssh -i ~/.ssh/azure_qwen -o ConnectTimeout=10 eduboost@<IP>
```

## Cost Control

```bash
# Schedule auto-shutdown (6 PM UTC)
az vm auto-shutdown --resource-group qwen-rg --name qwen-coder-14b --time 1800

# Check current VM size and cost
az vm show --resource-group qwen-rg --name qwen-coder-14b --query hardwareProfile.vmSize

# Resize to smaller (must deallocate first)
az vm deallocate --resource-group qwen-rg --name qwen-coder-14b
az vm resize --resource-group qwen-rg --name qwen-coder-14b --size Standard_B2s
az vm start --resource-group qwen-rg --name qwen-coder-14b
```

## Cleanup

```bash
# Delete entire resource group
az group delete --name qwen-rg --yes
```

## Key Files

| File | Purpose |
|------|---------|
| `bicep/qwen_gpu_vm.bicep` | Azure infrastructure template |
| `bicep/qwen_gpu_vm.parameters.json` | Deployment parameters |
| `scripts/setup_qwen_gpu_vm.sh` | VM setup automation |
| `docs/QWEN_DEPLOYMENT.md` | Full deployment guide |
| `docs/QWEN_QUICK_REFERENCE.md` | This file |

## Typical Flow

1. Edit `bicep/qwen_gpu_vm.parameters.json` with your SSH key
2. Deploy: `az deployment group create ...`
3. Get IP: `az vm show ...`
4. SSH in: `ssh -i key eduboost@IP`
5. Start Ollama: `sudo systemctl start ollama`
6. Pull model: `ollama pull qwen2.5-coder:14b` (wait 15-30 min)
7. Test: `curl http://localhost:11434/api/generate ...`
8. Integrate with EduBoost: Use Ollama API endpoint

## VM Sizes Comparison

| Size | GPU | VRAM | System RAM | Cost/hr | Best For |
|------|-----|------|-----------|---------|----------|
| Standard_NC4as_T4_v3 | 1x T4 | 16GB | 28GB | ~$0.35 | **Starting point** - Good for 4-bit |
| Standard_NC8as_T4_v3 | 2x T4 | 32GB | 56GB | ~$0.70 | Higher throughput, batch inference |
| Standard_NC6s_v3 | 1x V100 | 32GB | 112GB | ~$0.90 | FP16 precision, lower quantization |

Start with `NC4as_T4_v3`. Upgrade if you need higher throughput or FP16.
