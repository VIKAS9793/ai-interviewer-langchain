# 🔧 Troubleshooting Guide

> **Last Updated:** 2025-12-07

## 🤖 Ollama & Model Issues

### "LLM connection failed" / "Connection refused"
*   **Cause:** The Ollama service is not running.
*   **Fix:** Open a separate terminal and run `ollama serve`. Ensure it is listening on port 11434.

### "Model not found"
*   **Cause:** You haven't downloaded the specific model required (`llama3.2:3b`).
*   **Fix:** Run `ollama pull llama3.2:3b`.

### Slow Responses / High Latency
*   **Cause:** Your system might be running on CPU only, or RAM is insufficient.
*   **Fix:** Ensure you have at least 4GB of free RAM. If you have an NVIDIA GPU, ensure CUDA drivers are installed so Ollama can use it.

---

## 🌐 Web Interface Issues

### Interface doesn't load
*   **Cause:** Port 7860 might be blocked by a firewall or another application.
*   **Fix:** The application logs will show the URL. Try accessing `http://127.0.0.1:7860` specifically.

### "Queue is full"
*   **Cause:** Too many requests are being processed simultaneously.
*   **Fix:** The system handles concurrent requests, but local hardwar limits may apply. Wait a moment and try again.

---

## 🧠 Brain / Memory Issues

### "Database locked"
*   **Cause:** Multiple instances of the application might be trying to write to `data/memory/reasoning_bank.db`.
*   **Fix:** Ensure only one instance of `python main.py` is running.

### Resetting the AI's Brain
*   **Goal:** You want to clear all learned strategies and start fresh.
*   **Action:** Delete the contents of the `data/memory/` directory (but keep the directory itself).
    ```bash
    rm data/memory/*.db data/memory/*.json
    ```
    The system will recreate them automatically on next run.
