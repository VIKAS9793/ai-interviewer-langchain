# Setup Guide

> Complete setup instructions for the AI Technical Interviewer v4.7

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required |
| Node.js | 18+ | Required for A2UI frontend |
| Google API Key | - | [Get free key](https://aistudio.google.com/app/apikey) |
| Git | 2.0+ | For cloning |

---

## Quick Start (ADK Dev UI Only)

For basic testing without the A2UI frontend:

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

> **Note:** If `adk` command is not found after installation, run:
> ```bash
> pip install google-adk
> ```

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

## Full Setup (A2UI Frontend - v4.7)

For the complete A2UI experience with beautiful web interface:

### Prerequisites (Additional)

```bash
# Clone A2UI repository (if not already present)
git clone https://github.com/AmpereComputing/a2ui.git a2ui-repo

# Install frontend dependencies
cd a2ui-repo/samples/client/lit/shell
npm install
cd ../../../..
```

### Running All 3 Services

You need **3 terminals** running simultaneously:

#### Terminal 1: ADK Backend
```bash
# From project root
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # macOS/Linux

python -m google.adk.cli web ./src
```
✅ Should show: `ADK Web Server started` at `http://127.0.0.1:8000`

#### Terminal 2: A2A-ADK Bridge
```bash
# From project root (new terminal)
.venv\Scripts\activate

python -m src.adk_interviewer.a2ui.bridge
```
✅ Should show: `Bridge: http://localhost:10002`

#### Terminal 3: A2UI Frontend
```bash
# From project root (new terminal)
cd a2ui-repo/samples/client/lit/shell

# Important: Use npx directly, NOT npm run dev (Windows compatibility)
npx vite dev --port 3000 --open "/?app=interviewer"
```
✅ Browser should auto-open to: `http://localhost:3000/?app=interviewer`

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    A2UI Frontend (Lit)                       │
│  localhost:3000/?app=interviewer                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ A2A Protocol (JSON-RPC 2.0)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 A2A-ADK Bridge (FastAPI)                     │
│  localhost:10002                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ ADK Protocol (REST + SSE)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADK Backend (Gemini)                      │
│  localhost:8000                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Using the Interviewer

1. **Select Agent:** Choose `adk_interviewer` from dropdown (ADK UI) or use A2UI
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

### `adk` Command Not Found
```
'adk' is not recognized as an internal or external command
```
**Solution:** Install the ADK package:
```bash
pip install google-adk
```
Or use the full Python module path:
```bash
python -m google.adk.cli web ./src
```

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

### A2UI Frontend - `npm run dev` Fails on Windows
```
wireit: spawn sh ENOENT
```
**Root Cause:** The `wireit` build tool uses Linux-style shell commands.

**Solution:** Use `npx vite dev` directly instead of `npm run dev`:
```bash
npx vite dev --port 3000 --open "/?app=interviewer"
```

### Bridge Returns 500 Error
```
ERROR:__main__:Error processing request: Expecting value
```
**Possible Causes:**
1. ADK returned a function call (internal routing) - handled in v4.7.1+
2. Rate limit exceeded - wait and retry

**Solution:** Ensure you're using the latest bridge code from `src/adk_interviewer/a2ui/bridge.py`

### Tool 'execute_python_code' Not Found
```
ValueError: Tool 'execute_python_code' not found
```
**Root Cause:** Coding agent instruction implied code execution capability.

**Solution:** Fixed in v4.7.1 - the `coding_agent.py` now explicitly states "NO CODE EXECUTION".

### Rate Limit (429 Error)
```
429 Too Many Requests
```
**Solution:** Wait 1-2 minutes before retrying. Free tier has limited RPM.

---

## Version History

| Version | Features |
|---------|----------|
| v4.7.1 | Fixed coding agent tool hallucination, bridge error handling |
| v4.7.0 | A2UI integration (experimental) |
| v4.6.0 | Sequential Safety pattern |
| v4.5.0 | Root agent orchestration |

---

## Next Steps

- [Architecture Guide](ARCHITECTURE.md)
- [A2UI Integration Journey](A2UI_INTEGRATION_JOURNEY.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing](CONTRIBUTING.md)