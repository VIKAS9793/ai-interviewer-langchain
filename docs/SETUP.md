# 🛠️ Setup & Installation Guide

> **Last Updated:** 2025-12-10
> **Version:** 2.3.1 (Stability Patch)

## 📋 Prerequisites

1. **Python 3.11+**: [Download Here](https://www.python.org/downloads/)
2. **HuggingFace Account**: [Sign Up Here](https://huggingface.co/join)
3. **HuggingFace API Token**: [Get Token](https://huggingface.co/settings/tokens)

> [!NOTE]
> This application runs on **HuggingFace Spaces** or locally with the HuggingFace Inference API. No local GPU or Ollama required.

---

## ☁️ Option 1: HuggingFace Spaces (Recommended)

The easiest way to use the AI Interviewer:

1. Visit: **https://huggingface.co/spaces/Vikas9793/ai-interviewer**
2. Enter your name and select a topic
3. Start your interview!

No installation required.

---

## 💻 Option 2: Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain
git checkout cloud  # Use cloud branch
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

### 4. Configure API Token
```bash
# Windows (PowerShell)
$env:HF_TOKEN = "your_huggingface_token"

# macOS / Linux
export HF_TOKEN="your_huggingface_token"
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
| Model loading slow | First request may take 30-60s for model warmup |
| 401 Unauthorized | Check HF_TOKEN is set correctly |
| Rate limited | Wait 1 minute or upgrade HuggingFace account |
| Port 7860 in use | App auto-finds next available port |

---

## 🧪 Verification

Test your installation:
```bash
pytest tests/ -v
```
