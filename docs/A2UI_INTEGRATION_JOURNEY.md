# A2UI Integration Journey: From Simple ADK to Beautiful Web UI

**Version:** 4.7.0 (Experimental)  
**Date:** December 24, 2025  
**Branch:** dev/a2ui-integration

---

## Executive Summary

This document chronicles our journey integrating Google's A2UI (Agent-to-User Interface) protocol with the AI Interviewer project, transforming a basic ADK terminal interface into a beautiful, modern web UI.

> **Result:** Successfully bridged two incompatible protocols to render AI Interviewer responses in a rich, component-based web interface.

---

## The Vision

### What We Wanted

| Before | After |
|--------|-------|
| Plain text in ADK dev-ui | Rich components in modern web UI |
| Terminal-like experience | Beautiful gradient backgrounds |
| Copy-paste code snippets | Syntax-highlighted code editors |
| Static Q&A | Interactive buttons, forms, cards |

### Why A2UI?

A2UI is Google's streaming protocol for AI agents to dynamically render platform-agnostic UIs. Perfect for technical interviews where we need:

- **Code editors** with syntax highlighting
- **Question cards** with difficulty badges
- **Feedback panels** with scores
- **Interactive elements** for candidate responses

---

## The Challenge

### Protocol Mismatch

When we started, we discovered a fundamental incompatibility:

```
A2UI Frontend (Lit)     ADK Backend
      │                      │
      │ A2A Protocol         │ ADK Protocol
      │ (JSON-RPC)           │ (REST sessions)
      │                      │
      ├───────── ✗ ──────────┤
      │   INCOMPATIBLE!      │
```

**A2UI uses A2A Protocol:**
- JSON-RPC 2.0 format
- `/.well-known/agent-card.json` discovery
- `POST /` with `message/send` method
- Expects `ServerToClientMessage[]` with A2UI components

**ADK uses different endpoints:**
- REST API at `/apps/{app}/users/{user}/sessions/{id}`
- SSE streaming at `/run_sse`
- Different message format

---

## The Approach: Protocol Bridge

We built a **FastAPI bridge server** that translates between protocols:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  A2UI Frontend  │────▶│  A2A-ADK Bridge │────▶│  ADK Backend    │
│  :3000          │     │  :10002         │     │  :8000          │
│  (Lit + Vite)   │     │  (FastAPI)      │     │  (Gemini)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       A2A ←──────────────────────────────────────────→ ADK
```

### Bridge Responsibilities

1. **Agent Card Discovery** - Expose `/.well-known/agent-card.json`
2. **Request Translation** - A2A JSON-RPC → ADK REST
3. **Session Management** - Create ADK sessions
4. **Response Parsing** - SSE text → A2UI components
5. **Format Compliance** - JSON-RPC 2.0 response wrapper

---

## Engineering Challenges & Solutions

### Challenge 1: Missing Endpoints (404s)

**Problem:** Initial attempts returned 404 on `/run` and `/apps/.../messages`.

**Investigation:** ADK web server uses different endpoints than `adk api_server`.

**Solution:** Use `/run_sse` with session creation first.

```python
# Step 1: Create session
POST /apps/{app}/users/{user}/sessions/{session_id}

# Step 2: Send message
POST /run_sse with app_name, user_id, session_id, new_message
```

---

### Challenge 2: SSE Response Parsing

**Problem:** ADK returns Server-Sent Events, not JSON.

**Format:**
```
data: {"modelVersion":"gemini-2.5-flash-lite","content":{"parts":[{"text":"..."}]}}
```

**Solution:** Parse SSE `data:` lines, extract text from nested structure.

---

### Challenge 3: A2UI Component Format

**Problem:** UI showed blank screen despite receiving responses.

**Investigation:** Multiple format issues discovered:

| Issue | Wrong | Correct |
|-------|-------|---------|
| surfaceId location | Sibling of beginRendering | Inside beginRendering |
| Component key | `componentProperties` | `component` |
| Text value | Plain string | `{literalString: ...}` |

**Solution:** Studied spec at `specification/0.8/json/server_to_client.json`, fixed all three issues.

---

### Challenge 4: JSON-RPC Response Format

**Problem:** A2UI client ignored responses, returned to welcome screen.

**Root cause:** A2A uses JSON-RPC 2.0 which requires `id` field matching request.

**Solution:**
```python
return {
    "jsonrpc": "2.0",
    "id": request.get("id", 1),  # Must match request id!
    "result": {...}
}
```

---

### Challenge 5: Windows Build Compatibility

**Problem:** A2UI Lit renderer uses wireit with Linux-style copy commands.

**Solution:** Manually copied schema files and ran TypeScript directly:
```powershell
Copy-Item "..\..\specification\0.8\json\*.json" "src\0.8\schemas\"
npx tsc -b --pretty
```

---

## What Worked

✅ **Cloning A2UI repo** - 65MB, full samples and Lit renderer  
✅ **Custom config** - `interviewer.ts` with Google-inspired gradient  
✅ **Session management** - Proper ADK session creation  
✅ **SSE parsing** - Extracted text from streaming response  
✅ **A2UI components** - Column → Text rendering working  
✅ **JSON-RPC compliance** - Proper id/jsonrpc fields  

---

## What Failed Initially

❌ **Direct ADK connection** - Protocol mismatch  
❌ **Wrong endpoints** - Trial and error on /run vs /run_sse  
❌ **componentProperties** - Wrong key name from older docs  
❌ **Missing literalString** - Text display blank  
❌ **Missing JSON-RPC id** - Response ignored by client  

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| A2UI breaking changes | Pinned to v0.8.1 |
| ADK API changes | Bridge abstracts protocol |
| Security (untrusted UI) | Local development only |
| Performance (3 servers) | Production would consolidate |

---

## Final Architecture

```
User Browser
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                    A2UI Frontend (Lit)                       │
│  localhost:3000/?app=interviewer                            │
│  • Vite dev server                                          │
│  • Custom interviewer.ts config                             │
│  • Google-inspired gradient background                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ A2A Protocol (JSON-RPC 2.0)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 A2A-ADK Bridge (FastAPI)                     │
│  localhost:10002                                            │
│  • /.well-known/agent-card.json                             │
│  • POST / → ADK /run_sse translation                        │
│  • Text → A2UI Column/Text component generation             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ ADK Protocol (REST + SSE)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADK Backend (Gemini)                      │
│  localhost:8000                                             │
│  • adk web ./src                                            │
│  • AI Interviewer agent                                     │
│  • Sequential Safety pattern                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Files Created

| File | LOC | Purpose |
|------|-----|---------|
| `src/adk_interviewer/a2ui/bridge.py` | 385 | Protocol bridge server |
| `src/adk_interviewer/a2ui/components.py` | 182 | A2UI component schemas |
| `a2ui-repo/samples/client/lit/shell/configs/interviewer.ts` | 45 | Frontend config |

---

## How to Run

```bash
# Terminal 1: ADK Backend
.\.venv\Scripts\adk web ./src

# Terminal 2: A2A Bridge
.\.venv\Scripts\python -m src.adk_interviewer.a2ui.bridge

# Terminal 3: A2UI Frontend
cd a2ui-repo/samples/client/lit/shell
npx vite dev --port 3000

# Open browser
http://localhost:3000/?app=interviewer
```

---

## Lessons Learned

1. **Protocol bridges solve incompatibility** - When two systems don't speak the same language, translate
2. **Read the spec thoroughly** - Small format differences cause silent failures
3. **Logs are essential** - Bridge logging revealed every issue
4. **Iterate quickly** - Multiple hot-fixes, instant feedback
5. **Don't give up** - "Do hard engineering" mindset prevailed

---

## Next Steps

- [ ] Add TextField for user input
- [ ] Maintain session across turns
- [ ] Render code with syntax highlighting
- [ ] Add Button components for actions
- [ ] Production deployment consolidation

---

## Conclusion

What started as "A2UI uses different protocol than ADK" became a successful integration through careful engineering. The bridge pattern proved effective, and the foundation is now in place for rich, interactive AI-powered interviews.

**From terminal to beautiful web UI - mission accomplished.** 🎉
