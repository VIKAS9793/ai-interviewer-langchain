# Deployment Guide

AI Interviewer runs anywhere - local, Docker, Kubernetes, or cloud.

## Quick Start

### Option 1: Local (Development)
```bash
# 1. Create .env from template
cp .env.example .env
# Add your GOOGLE_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run ADK server
adk web src/adk_interviewer

# 4. Run A2A Bridge (new terminal)
python src/adk_interviewer/a2ui/bridge.py

# 5. Run A2UI Frontend (new terminal)
cd a2ui-repo/samples/client/lit/shell
npm install && npx vite dev --port 3000

# 6. Open http://localhost:3000/?app=interviewer
```

### Option 2: Docker Compose
```bash
# 1. Create .env
cp .env.example .env

# 2. Start all services
docker-compose up

# 3. Open http://localhost:3000/?app=interviewer
```

### Option 3: Docker Only
```bash
# Build image
docker build -t ai-interviewer .

# Run ADK
docker run -p 8000:8000 -e GOOGLE_API_KEY=xxx ai-interviewer
```

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   A2UI      │────▶│   Bridge    │────▶│    ADK      │
│  Frontend   │     │  (10002)    │     │   (8000)    │
│   (3000)    │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | - | Gemini API key |
| `ADK_PORT` | ❌ | 8000 | ADK server port |
| `BRIDGE_PORT` | ❌ | 10002 | Bridge port |
| `FRONTEND_PORT` | ❌ | 3000 | Frontend port |
