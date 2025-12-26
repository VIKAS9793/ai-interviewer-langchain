# Architecture Documentation

**AI Technical Interviewer - v4.7.1**

---

## Overview

Multi-agent architecture using Google ADK's sub_agents pattern. 6 specialized agents orchestrated by a root agent, with optional multi-dimensional scoring system. v4.7 adds experimental A2UI web interface with protocol bridge.

---

## System Architecture

### High-Level Design (v4.7.1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Option A: ADK Dev UI          Option B: A2UI Frontend (v4.7)      │
│   http://localhost:8000         http://localhost:3000               │
│   (Built-in terminal UI)        (Beautiful web UI)                  │
│                                                                     │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      │                                                       │
      ▼                                                       ▼
┌─────────────────┐                           ┌─────────────────────────┐
│   ADK Backend   │◀──────────────────────────│   A2A-ADK Bridge       │
│   :8000         │       REST + SSE          │   :10002               │
│   (Direct)      │                           │   (Protocol Translator) │
└────────┬────────┘                           └───────────────────────┬─┘
         │                                                            │
         │                                    ┌─────────────────────────┐
         │                                    │   A2UI Lit Renderer    │
         │                                    │   :3000                │
         │                                    │   (JSON-RPC 2.0 / A2A) │
         │                                    └─────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ADK Web Server (:8000)                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────────────┐    │
│  │   Web UI    │  │ Session Service  │  │  run_sse / HTTP API │    │
│  └─────────────┘  └──────────────────┘  └──────────┬──────────┘    │
└────────────────────────────────────────────────────┼────────────────┘
                                                     │
                                                     ▼
                  ┌────────────────────────────────────────────┐
                  │      root_agent (Orchestrator)             │
                  │  Routes tasks to specialist sub-agents     │
                  └───────────────┬────────────────────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            │         6 Specialist Sub-Agents           │
            ├───────────────────────────────────────────┤
            │ • interviewer_agent (Questions/Eval)      │
            │ • resume_agent     (Resume/JD Analysis)   │
            │ • coding_agent     (Code Analysis v4.7.1) │──▶ Gemini 2.5 Flash-Lite
            │ • safety_agent     (Content Moderation)   │
            │ • study_agent      (Guided Learning)      │
            │ • critic_agent     (Answer Critique)      │
            └───────────────────────────────────────────┘
```

### Multi-Agent Flow Visualization

<p align="center">
  <img src="../assets/multi_agent_flow.png" alt="Multi-Agent Orchestration Flow" width="600"/>
</p>

---


## A2UI Integration (v4.7)

### Three-Tier Architecture

| Tier | Component | Port | Protocol |
|------|-----------|------|----------|
| **Frontend** | A2UI Lit Renderer | 3000 | A2A (JSON-RPC 2.0) |
| **Bridge** | A2A-ADK FastAPI Server | 10002 | Bidirectional translation |
| **Backend** | ADK Web Server | 8000 | REST + SSE |

### Protocol Translation

The A2A-ADK Bridge handles:

1. **Agent Discovery** - Exposes `/.well-known/agent-card.json`
2. **Request Translation** - A2A JSON-RPC → ADK REST
3. **Session Management** - Creates and maintains ADK sessions
4. **Response Parsing** - SSE text → A2UI components
5. **Error Handling** - Graceful fallbacks for edge cases

### Why a Bridge?

A2UI uses A2A Protocol (JSON-RPC 2.0), while ADK uses REST endpoints. Direct connection is impossible, so the bridge translates between them.

---

## Agent Specifications

### 1. root_agent (Orchestrator)
**Type:** Coordinator  
**Model:** Gemini 2.5 Flash-Lite  
**Purpose:** Main entry point, routes requests to specialists

**Sub-Agents:**
- interviewer_agent
- resume_agent
- coding_agent
- safety_agent
- study_agent
- critic_agent

---

### 2. interviewer_agent
**Type:** Question Generation & Evaluation  
**Tools:** 2 custom tools

**Capabilities:**
- Generate adaptive interview questions
- Evaluate candidate answers with CoT reasoning
- Provide detailed feedback
- Adjust difficulty based on performance

**Tools:**
- `generate_question(topic, difficulty, context)`
- `evaluate_answer(question, answer, rubric)`

---

### 3. resume_agent
**Type:** Document Analysis  
**Tools:** 2 custom tools  
**File Support:** PDF, DOCX, TXT (via ADK artifacts)

**Capabilities:**
- Parse resume text from pasted content
- Load uploaded files via ADK artifact system
- Extract text from PDF files (PyPDF2)
- Extract text from DOCX files (python-docx)
- Extract skills, experience, education
- Generate candidate summary

**Tools:**
- `parse_resume(resume_text, tool_context)` - **Supports file upload via artifacts**
- `analyze_job_description(jd_text, tool_context)`

---

### 4. coding_agent (v4.7.1)
**Type:** Code Analysis (Manual Tracing Only)  
**Tools:** None (pure LLM reasoning)

> **IMPORTANT (v4.7.1):** This agent does NOT execute code. It analyzes code by reading and reasoning about it manually.

**Capabilities:**
- Trace code logic step by step mentally
- Identify potential issues or bugs
- Assess time/space complexity
- Explain what code does
- Suggest improvements

**Limitations:**
- Cannot execute code (ADK sub-agent tool limitation)
- Cannot run test cases (traces manually instead)
- Safety checks delegated to safety_agent

**Why No Code Execution?**
ADK sub-agents have a known limitation: "Tool use with function calling is unsupported" when used in sub-agents. This caused the `execute_python_code` tool hallucination bug in v4.7.0, fixed in v4.7.1 by explicitly stating in the instruction that no tools are available.

---

### 5. safety_agent
**Type:** Content Moderation  
**Tools:** LLM reasoning

**Capabilities:**
- Detect bias and discrimination
- Flag inappropriate content
- Monitor for PII leakage
- Ensure fair interviews

---

### 6. study_agent
**Type:** Educational Tutor  
**Tools:** 2 custom tools

**Capabilities:**
- Explain ANY interview topic (not limited to CS)
- Provide progressive hints (3 levels)
- Socratic method teaching
- Dynamic explanations using Gemini's knowledge
- Never gives direct solutions

**Topics Covered:**
- Technical/Engineering (algorithms, system design)
- Product Management (product sense, metrics)
- Business/Strategy (market analysis, revenue)
- Behavioral (leadership, teamwork)
- Design (UX/UI principles)
- Data/Analytics (SQL, A/B testing)
- Any other topic via Gemini's knowledge

**Tools:**
- `explain_concept(topic, depth)` - Works for ANY topic
- `provide_hints(question, approach, level)`

---

### 7. critic_agent
**Type:** Quality Assurance  
**Tools:** LLM reasoning

**Capabilities:**
- Validate question quality
- Critique candidate answers
- Suggest improvements
- Ensure fairness

---

## Optional: Multi-Agent Scoring System

### scoring_coordinator
**Type:** Evaluation Orchestrator  
**Sub-Agents:** 3 specialist scorers

**Architecture:**
```
scoring_coordinator
  ├── technical_scorer      (40% weight)
  ├── communication_scorer  (30% weight)
  └── problem_solving_scorer (30% weight)
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Google ADK | Latest |
| LLM | Gemini 2.5 Flash-Lite | Latest |
| Language | Python | 3.11+ |
| Web Server | ADK Web | Built-in |
| State | ADK SessionService | Built-in |
| A2UI Frontend | Lit + Vite | v7.3+ |
| Bridge | FastAPI + httpx | v0.115+ |

---

## Known Limitations

### ADK Sub-Agent Tool Limitation
Sub-agents in ADK have restricted tool calling capabilities. Tools that work in root agents may fail in sub-agents with:
```
Tool use with function calling is unsupported
```

**Workaround:** Use pure LLM reasoning for sub-agents, or move tool-dependent logic to root agent.

### Windows Compatibility
The A2UI `wireit` build system uses Linux-style shell commands. On Windows:
- Use `npx vite dev` directly instead of `npm run dev`
- Manually copy schema files if needed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v4.7.1 | Dec 2025 | Fixed coding_agent tool hallucination, bridge error handling |
| v4.7.0 | Dec 2025 | A2UI integration (experimental) |
| v4.6.0 | Dec 2025 | Sequential Safety pattern |
| v4.5.2 | Dec 2025 | Study agent ANY-topic support |
| v4.5.0 | Dec 2025 | Root agent orchestration |
| v4.4.0 | Dec 2025 | Difficulty modes |
| v4.3.0 | Dec 2025 | Multi-agent scoring |

---

## Future Enhancements

- Rich A2UI components (code blocks, buttons, cards)
- Streaming responses in A2UI
- Code execution sandbox (secure container)
- Voice Interview (Gemini Live)
- Visual System Design (Diagrams)
- Multi-language Support

---

**For implementation details, see source code in `src/adk_interviewer/`**
