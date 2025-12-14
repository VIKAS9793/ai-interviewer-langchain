# 🛠️ Setup & Installation Guide

> **Last Updated:** 2025-12-14
> **Version:** 3.2.1 (Hybrid LLM + Pydantic Structured Output)

## 📋 Prerequisites

1. **Python 3.11+**: [Download Here](https://www.python.org/downloads/)
2. **HuggingFace Account**: [Sign Up Here](https://huggingface.co/join)
3. **OpenAI API Key** (Optional, for best experience): [Get Here](https://platform.openai.com/api-keys)
4. **Docker** (Optional, recommended for production)

> [!NOTE]
> This application supports **hybrid LLM mode**: OpenAI (paid, best quality) or HuggingFace (free, good quality). Works with either or both.

---

## ☁️ Option 1: HuggingFace Spaces (Recommended)

The easiest way to use the AI Interviewer:

1. Visit: **https://huggingface.co/spaces/Vikas9793/ai-interviewer**
2. Enter your name and select a topic.
3. Start your interview!

---

## 🐳 Option 2: Docker (Production-Ready)

This ensures you run the exact environment deployed to the cloud.

```bash
# Build the container
docker build -t ai-interviewer .

# Run the container (Exposes port 7860)
docker run -p 7860:7860 \
  -e HF_TOKEN="your_huggingface_token" \
  -e OPENAI_API_KEY="your_openai_key" \
  ai-interviewer
```

Access at: `http://localhost:7860`

---

## 💻 Option 3: Local Dev Environment

### 1. Clone the Repository
```bash
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain
# Main branch contains the stable v3.0 release
```

### 2. Set Up Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Tokens
```bash
# Required: HuggingFace Token (free)
# Windows (PowerShell)
$env:HF_TOKEN = "your_huggingface_token"

# macOS / Linux
export HF_TOKEN="your_huggingface_token"

# Optional: OpenAI API Key (for best experience)
$env:OPENAI_API_KEY = "sk-your-openai-key"  # Windows
export OPENAI_API_KEY="sk-your-openai-key"  # macOS/Linux
```

### 5. Run the Application
```bash
python main.py
```

The web interface launches at: `http://localhost:7860`

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| **Model loading slow** | First request may take 30-60s for model warmup |
| **401 Unauthorized** | Check `HF_TOKEN` is set correctly |
| **403 Forbidden** | Ensure your HF Token has `write` permissions (if pushing) or `read` (if using inference) |
| **Port 7860 in use** | App auto-finds next available port |

---

## 🧪 Verification

Test your installation:
```bash
pytest tests/ -v
```
