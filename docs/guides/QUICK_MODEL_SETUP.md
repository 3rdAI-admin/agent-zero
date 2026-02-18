# Quick Model Setup for Penetration Testing

## Current Status
Your settings show OpenAI models, but you should be using Ollama. Let's fix this.

## Best Models for Pen Testing (From Your Available Models)

### 🚀 Speed-Optimized (Fast Command Execution)
**Best for:** Quick tool execution, rapid testing, many commands
```
Chat Model:    phi3:latest (3.8B - fast)
Utility Model:  gemma3:1b (1B - very fast)
Browser Model:  qwen3:latest (8.2B - good for web)
```

### ⚖️ Balanced (Recommended)
**Best for:** Good reasoning with reasonable speed
```
Chat Model:    qwen3:latest (8.2B - current, good)
Utility Model:  phi3:latest (3.8B - faster for utilities)
Browser Model:  qwen3:latest (8.2B - consistent)
```

### 🧠 Maximum Capability
**Best for:** Complex multi-step attacks, detailed analysis
```
Chat Model:    gemma3:27b (27.4B - powerful)
Utility Model:  qwen3:latest (8.2B)
Browser Model:  llava:7b (7B - vision for screenshots)
```

## Quick Setup Script

Run this to set up the **Balanced** configuration:

```bash
cd /home/kali/Tools/agent-zero
python3 << 'EOF'
import json
from python.helpers import files

settings_file = files.get_abs_path('tmp/settings.json')
with open(settings_file, 'r') as f:
    s = json.load(f)

# Set to Ollama with balanced models
s['chat_model_provider'] = 'ollama'
s['chat_model_name'] = 'qwen3:latest'
s['chat_model_api_base'] = 'http://192.168.50.7:11434'

s['util_model_provider'] = 'ollama'
s['util_model_name'] = 'phi3:latest'
s['util_model_api_base'] = 'http://192.168.50.7:11434'

s['browser_model_provider'] = 'ollama'
s['browser_model_name'] = 'qwen3:latest'
s['browser_model_api_base'] = 'http://192.168.50.7:11434'

with open(settings_file, 'w') as f:
    json.dump(s, f, indent=2)

print("✅ Models configured!")
print("  Chat:    qwen3:latest")
print("  Utility: phi3:latest")
print("  Browser: qwen3:latest")
print("\nRestart Agent Zero: ./startup.sh")
EOF
```

## Why These Models?

### For Command Execution (Terminal)
- **phi3:latest** or **gemma3:1b**: Fast responses, good for tool orchestration
- Lower latency = faster penetration testing workflow

### For Analysis & Planning
- **qwen3:latest**: Strong reasoning, understands complex security scenarios
- Good at following multi-step attack chains

### For Browser Automation
- **qwen3:latest**: Good at understanding web pages
- **llava:7b**: If you need vision capabilities for screenshots

### For Utility Tasks
- **phi3:latest** or **gemma3:1b**: Fast for memory operations, summarization
- Saves resources for main chat model

## Performance Comparison

| Model | Size | Speed | Reasoning | Best For |
|-------|------|-------|-----------|----------|
| gemma3:1b | 1B | ⚡⚡⚡ | ⭐⭐ | Quick commands |
| phi3:latest | 3.8B | ⚡⚡ | ⭐⭐⭐ | Balanced |
| qwen3:latest | 8.2B | ⚡ | ⭐⭐⭐⭐ | Main chat |
| gemma3:27b | 27.4B | 🐌 | ⭐⭐⭐⭐⭐ | Complex analysis |

## Testing Your Setup

After configuring, test with:
```
"Run nmap -sV -p 80,443 192.168.50.7 and analyze the results"
```

A good model will:
- ✅ Execute the command correctly
- ✅ Parse output accurately  
- ✅ Suggest follow-up actions
- ✅ Handle errors gracefully

