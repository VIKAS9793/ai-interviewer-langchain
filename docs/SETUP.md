# 🛠️ Setup & Installation Guide

> **Last Updated:** 2025-12-07
> **Version:** 2.0.0

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.11+**: [Download Here](https://www.python.org/downloads/)
2.  **Git**: [Download Here](https://git-scm.com/downloads)
3.  **Ollama**: [Download Here](https://ollama.ai/)

---

## 💻 Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain
```

### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

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
We use a strictly pinned dependency list for stability.
```bash
pip install -r requirements.txt
```

### 4. Configure AI Model
The system uses `llama3.2:3b` by default for the best balance of speed and reasoning.

```bash
# Pull the model
ollama pull llama3.2:3b

# Verify it's ready
ollama list
```

---

## 🚀 Running the Application

Start the autonomous interviewer:
```bash
python main.py
```

The web interface will launch automatically at:
`http://localhost:7860`

---

## ⚠️ Common Configuration Issues

*   **Port Conflicts:** If port 7860 is taken, the app will try to find the next available port (e.g., 7861). Check the console output for the actual URL.
*   **Ollama Connection:** Ensure Ollama is running (`ollama serve`). The app connects to `localhost:11434`.

---

## 🧪 Verification
To verify your installation is correct, you can run the test suite:
```bash
pytest tests/test_production.py
```
