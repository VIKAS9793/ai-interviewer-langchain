# Setup Guide

> Complete setup instructions for the AI Technical Interviewer

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required |
| Google API Key | - | [Get free key](https://aistudio.google.com/app/apikey) |
| Git | 2.0+ | For cloning |

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/VIKAS9793/ai-interviewer-google-adk.git
cd ai-interviewer-google-adk
git checkout google-adk
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
# Copy template
cp .env.example .env

# Edit .env file
# Add: GOOGLE_API_KEY=your_key_here
```

### 5. Run Application

```bash
adk web src
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Using the Interviewer

1. **Select Agent:** Choose `adk_interviewer` from dropdown
2. **Start Chat:** Type your message to begin
3. **Interview:** Answer questions, get real-time feedback
4. **Review:** See your scores and improvement areas

---

## Troubleshooting

### API Key Not Found
```
GOOGLE_API_KEY environment variable is required
```
**Solution:** Ensure `.env` file has your key and is UTF-8 encoded.

### Module Import Error
```
attempted relative import beyond top-level package
```
**Solution:** Run `adk web src` (not `adk web src/adk_interviewer`).

### Port Already in Use
```
Address already in use
```
**Solution:** Use a different port: `adk web src --port 8001`

---

## Next Steps

- [Architecture Guide](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing](../CONTRIBUTING.md)