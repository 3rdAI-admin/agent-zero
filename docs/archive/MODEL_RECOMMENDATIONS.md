# Model Recommendations for Penetration Testing in Agent Zero

## Current Configuration
- **Ollama URL**: http://192.168.50.7:11434
- **Current Model**: qwen3:latest

## Best Models for Penetration Testing

### 1. **Qwen2.5:72B or Qwen3:latest** (Current - Good Choice)
**Pros:**
- Excellent for technical tasks and code generation
- Strong reasoning capabilities
- Good at following complex instructions
- Handles security testing workflows well

**Cons:**
- Larger model (requires more RAM/VRAM)
- Slower inference speed

**Best for:** Complex penetration testing, multi-step attacks, report generation

### 2. **Llama 3.2:3B or Llama 3.1:8B** (Recommended for Speed)
**Pros:**
- Fast inference (quick responses)
- Good balance of capability and speed
- Lower resource requirements
- Excellent for command execution and tool usage

**Cons:**
- Less capable for complex reasoning
- May need more guidance for advanced techniques

**Best for:** Quick command execution, tool orchestration, rapid testing

### 3. **Mistral 7B or Mistral Large**
**Pros:**
- Strong technical understanding
- Good at security concepts
- Balanced performance

**Cons:**
- Medium resource requirements

**Best for:** General penetration testing tasks

### 4. **DeepSeek Coder or DeepSeek R1**
**Pros:**
- Excellent for code analysis
- Great for understanding exploits
- Strong technical reasoning

**Cons:**
- May be overkill for simple command execution

**Best for:** Code review, exploit development, complex analysis

## Recommended Configuration for Penetration Testing

### Option A: Speed-Optimized (Fast Response)
```
Chat Model:    llama3.2:3b or llama3.1:8b
Utility Model: llama3.2:3b (same)
Browser Model: llama3.2:3b (same)
```
**Use when:** You need quick responses, running many commands, rapid testing

### Option B: Balanced (Recommended)
```
Chat Model:    qwen3:latest or qwen2.5:72b
Utility Model: llama3.2:3b (faster for utility tasks)
Browser Model: qwen3:latest (better for browser automation)
```
**Use when:** You want good reasoning with reasonable speed

### Option C: Maximum Capability
```
Chat Model:    qwen2.5:72b or grok-2-LLM
Utility Model: qwen3:latest
Browser Model: qwen3:latest
```
**Use when:** Complex multi-step attacks, detailed analysis, report writing

## Model Selection Criteria

### For Command Execution (Terminal)
- **Priority**: Speed > Reasoning
- **Best**: Llama 3.2:3B, Llama 3.1:8B
- **Why**: Fast responses for tool orchestration

### For Analysis & Planning
- **Priority**: Reasoning > Speed
- **Best**: Qwen3:latest, Qwen2.5:72B, Grok-2
- **Why**: Better understanding of complex scenarios

### For Browser Automation
- **Priority**: Reasoning > Speed
- **Best**: Qwen3:latest, Mistral Large
- **Why**: Better at understanding web pages and interactions

### For Utility Tasks (Memory, Summarization)
- **Priority**: Speed > Reasoning
- **Best**: Llama 3.2:3B, Phi3:latest
- **Why**: Fast for simple tasks, saves resources

## Your Available Models

Based on your Ollama instance, you have:
- **llava:7b** - Vision model (good for screenshots/browser)
- **grok-2-LLM** - Very large, powerful (269.5B parameters)
- **kimi-k2:1t-cloud** - Large model
- **qwen3:latest** - Current choice, good balance
- **gemma3:1b** - Very fast, minimal resources
- **phi3:latest** - Fast, efficient
- **gpt-oss:20b** - Medium size
- **gemma3:27b** - Large, capable

## Quick Setup Guide

### To Change Models:

1. **Via Web UI (Recommended)**:
   - Open Settings → Agent tab
   - Change Chat Model, Utility Model, Browser Model
   - Click Save
   - Restart Agent Zero

2. **Via Settings File**:
   ```bash
   cd /home/kali/Tools/agent-zero
   python3 -c "
   import json
   with open('tmp/settings.json', 'r') as f:
       s = json.load(f)
   s['chat_model_name'] = 'llama3.2:3b'  # or your choice
   s['util_model_name'] = 'llama3.2:3b'
   s['browser_model_name'] = 'llama3.2:3b'
   with open('tmp/settings.json', 'w') as f:
       json.dump(s, f, indent=2)
   "
   ./startup.sh
   ```

## Performance Tips

1. **Use smaller models for utility tasks** - Saves resources
2. **Use larger models for main chat** - Better reasoning
3. **Match browser model to chat model** - Consistent behavior
4. **Monitor resource usage** - Adjust based on your hardware

## Testing Model Performance

Test with a simple command:
```
"Run nmap -sV -p 80,443 192.168.50.7"
```

**Good model will:**
- Execute command correctly
- Parse output accurately
- Suggest follow-up actions
- Handle errors gracefully

## Current Recommendation

For your setup (Kali VM, penetration testing):
- **Chat Model**: `qwen3:latest` (current - keep it)
- **Utility Model**: `phi3:latest` or `gemma3:1b` (faster)
- **Browser Model**: `qwen3:latest` (current - keep it)

This gives you good reasoning for complex tasks while keeping utility operations fast.

