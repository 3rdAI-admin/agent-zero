# Troubleshooting and FAQ
This page addresses frequently asked questions (FAQ) and provides troubleshooting steps for common issues encountered while using Agent Zero.

## Frequently Asked Questions
**1. How do I ask Agent Zero to work directly on my files or dirs?**
- Place the files/dirs in `/a0/usr`. Agent Zero will be able to perform tasks on them.

**2. When I input something in the chat, nothing happens. What's wrong?**
- Check if you have set up API keys in the Settings page. If not, the application cannot call LLM providers.

**3. I get “Invalid model ID.” What does that mean?**
- Verify the **provider** and **model naming**. For example, `openai/gpt-5.3` is correct for OpenRouter, but **incorrect** for the native OpenAI provider, which goes without prefix.

**4. Does ChatGPT Plus include API access?**
- No. ChatGPT Plus does not include API credits. You must provide an OpenAI API key in Settings.

**5. Where is chat history stored?**
- Chat history lives at `/a0/usr/chats/` inside the container.

**6. How do I integrate open-source models with Agent Zero?**
Refer to the [Choosing your LLMs](../setup/installation.md#installing-and-using-ollama-local-models) section for configuring local models (Ollama, LM Studio, etc.).

> [!TIP]
> Some LLM providers offer free usage tiers, for example Groq, Mistral, SambaNova, or CometAPI.

**7. How can I make Agent Zero retain memory between sessions?**
Use **Settings → Backup & Restore** and avoid mapping the entire `/a0` directory. See [How to update Agent Zero](../setup/installation.md#how-to-update-agent-zero).

**8. My browser agent fails or is unreliable. What now?**
The built-in browser agent is currently unstable on some systems. Use Skills or MCP alternatives such as Browser OS, Chrome DevTools, or Vercel's Agent Browser. See [MCP Setup](mcp-setup.md).

**9. My secrets disappeared after a backup restore.**
Secrets are stored in `/a0/usr/secrets.env` and are not always included in backup archives. Copy them manually.

**10. Where can I find more documentation or tutorials?**
- Join the Agent Zero [Skool](https://www.skool.com/agent-zero) or [Discord](https://discord.gg/B8KZKNsPpj) community.

**11. How do I adjust API rate limits?**
Use the model rate limit fields in Settings (Chat/Utility/Browser model sections) to set request/input/output limits. These map to the model config limits (for example `limit_requests`, `limit_input`, `limit_output`).

**12. My `code_execution_tool` doesn't work, what's wrong?**
- Ensure Docker is installed and running.
- On macOS, grant Docker Desktop access to your project files.
- Verify that the Docker image is updated.

**13. Can Agent Zero interact with external APIs or services (e.g., WhatsApp)?**
Yes, by creating custom tools or using MCP servers. See [Extensions](../developer/extensions.md) and [MCP Setup](mcp-setup.md).

## Troubleshooting

**Installation**
- **Docker Issues:** If Docker containers fail to start, consult the Docker documentation and verify your Docker installation and configuration.  On macOS, ensure you've granted Docker access to your project files in Docker Desktop's settings as described in the [Installation guide](../setup/installation.md#4-install-docker-docker-desktop-application). Verify that the Docker image is updated.
- **Web UI not reachable:** Ensure at least one host port is mapped to container port `80`. If you used `0:80`, check the assigned port in Docker Desktop.

**Usage**

- **Terminal commands not executing:** Ensure the Docker container is running and properly configured.  Check SSH settings if applicable. Check if the Docker image is updated by removing it from Docker Desktop app, and subsequently pulling it again.

* **Error Messages:** Pay close attention to the error messages displayed in the Web UI or terminal.  They often provide valuable clues for diagnosing the issue. Refer to the specific error message in online searches or community forums for potential solutions.

* **Performance Issues:** If Agent Zero is slow or unresponsive, it might be due to resource limitations, network latency, or the complexity of your prompts and tasks, especially when using local models.

* **Stuck on "Calling LLM...":** The UI shows this while the backend is waiting for the LLM (e.g. Ollama) to respond. If it never progresses:
  1. **Pause the agent** (use "Pause Agent" in the chat bar) so the run stops, then start a **new chat** and retry.
  2. **Check the LLM is reachable:** If using Ollama, ensure it is running and the API base in Settings matches where the container can reach it (e.g. `http://ollama:11434` if Ollama is in the same Docker network, or `http://host.docker.internal:11434` / `http://192.168.50.7:11434` if Ollama is on the host). From the host: `curl -s http://localhost:11434/api/tags` or open the API URL in a browser.
  3. **Ollama overloaded:** If the model is loading or the GPU is busy, the first token can take a long time. Wait a few minutes or restart Ollama, then retry.
  4. **Optional:** In **Settings → LiteLLM**, add a timeout (e.g. `request_timeout=120` or `stream_timeout=60`) so long-hanging calls eventually fail with an error instead of hanging indefinitely.
