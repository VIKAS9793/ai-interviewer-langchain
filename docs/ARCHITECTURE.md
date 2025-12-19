# Architecture

> System design and components of the AI Technical Interviewer

---

## Overview

```mermaid
flowchart TB
    subgraph "User Interface"
        A[ADK Web UI<br/>Port 8000]
    end
    
    subgraph "ADK Runtime"
        B[Session Service]
        C[Agent Runner]
    end
    
    subgraph "Agent Layer"
        D[AI Interviewer Agent]
    end
    
    subgraph "Google APIs"
        E[Gemini 2.5 Flash-Lite]
    end
    
    A --> B --> C --> D --> E
    E --> D --> C --> B --> A
```

---

## Components

### 1. ADK Web Server
- Built-in web interface from Google ADK
- Session management and state persistence
- Real-time streaming responses

### 2. Interviewer Agent
- Main LLM-powered agent
- Generates adaptive questions
- Evaluates answers with CoT reasoning
- Provides constructive feedback

### 3. Gemini Integration
- Native API calls (no wrapper)
- Model: `gemini-2.5-flash-lite`
- Streaming responses enabled

---

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant W as ADK Web
    participant A as Agent
    participant G as Gemini API
    
    U->>W: Send message
    W->>A: Forward to agent
    A->>G: LLM request
    G-->>A: Stream response
    A-->>W: Process & format
    W-->>U: Display response
```

---

## Directory Structure

```
src/
└── adk_interviewer/
    ├── agent.py          # Canonical root_agent entry point
    ├── main.py           # CLI/import validation
    ├── config/           # Configuration (ADKConfig)
    ├── tools/            # ADK-compliant tools (with ToolContext)
    ├── agents/           # Agent factories (critic, safety)
    ├── workflows/        # Multi-agent flows (SequentialAgent)
    └── utils/            # Reserved for future helpers
```

---

## Key Design Decisions

1. **Single Canonical Entry** - `agent.py` is the only `root_agent` definition
2. **ADK Best Practices** - Tools use `ToolContext` for state management
3. ** Built-in UI** - Leverage ADK's web interface (no custom UI)
4. **Stateful Tools** - Session state tracks questions, scores across turns
5. **Native Gemini** - Direct API calls for performance

---

## Security

- API keys in environment variables
- Google's native content filtering
- No PII storage in sessions
- HTTPS in production (Cloud Run)

---

## See Also

- [Setup Guide](SETUP.md)
- [Deployment Guide](DEPLOYMENT.md)
- [ADR-001: Migration to ADK](ADR/001-migration-to-google-adk.md)
