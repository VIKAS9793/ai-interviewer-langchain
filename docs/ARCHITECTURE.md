# Architecture Documentation

**AI Technical Interviewer - v4.6.0**

---

## Overview

Multi-agent architecture using Google ADK's sub_agents pattern. 6 specialized agents orchestrated by a root agent, with optional multi-dimensional scoring system.

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                      ADK Web Server                         │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   Web UI    │  │ Session Service  │  │  HTTP API    │  │
│  └─────────────┘  └──────────────────┘  └──────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
       ┌────────────────────────────────────────────┐
       │      root_agent (Orchestrator)             │
       │  Routes tasks to specialist sub-agents     │
       └───────────────┬────────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │    Specialist Sub-Agents    │
         ├────────────────────────────┤
         │ • interviewer_agent         │ ─┐
         │ • resume_agent              │  │
         │ • coding_agent              │  ├─▶ Gemini 2.5 Flash-Lite
         │ • safety_agent              │  │
         │ • study_agent               │  │
         │ • critic_agent              │ ─┘
         └─────────────────────────────┘
```

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

**File Upload Flow:**
1. User uploads PDF/DOCX via ADK Web UI
2. File saved as artifact automatically
3. Tool accesses `tool_context.artifacts`
4. Extracts text based on MIME type
5. Parses structured data

---

### 4. coding_agent (v4.6.0)
**Type:** Code Execution  
**Tools:** BuiltInCodeExecutor + Risk Assessment

**Capabilities:**
- Execute Python code in sandbox
- **Risk assessment before execution (v4.6.0)**
- **Blocks 10 dangerous patterns** (eval, exec, system calls, file ops, network)
- Verify algorithmic solutions
- Test code correctness
- Secure execution environment

**Sequential Safety Pattern:**
- Detects risky code before execution
- Logs blocked operations for security audit
- Provides safe alternatives when code blocked

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

### 6. study_agent (v4.2 → v4.5.2)
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

### 7. critic_agent (v4.5)
**Type:** Quality Assurance  
**Tools:** LLM reasoning

**Capabilities:**
- Validate question quality
- Critique candidate answers
- Suggest improvements
- Ensure fairness

---

## Optional: Multi-Agent Scoring System (v4.3)

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

**Weighted Aggregation:**
- Technical: Code correctness, quality, efficiency
- Communication: Clarity, structure, professionalism
- Problem-Solving: Approach, analytical thinking, creativity

**Output:** JSON-structured comprehensive assessment

---

## Difficulty Modes (v4.4)

### Quick Screen (15 min)
- 3-5 questions
- 70% easy, 30% medium
- Surface-level evaluation
- Binary pass/fail

### Standard Interview (45 min)
- 8-12 questions
- 25% easy, 50% medium, 25% hard
- Comprehensive assessment
- Multi-agent scoring

### Deep Technical (90 min)
- 15-20 questions
- 10% easy, 30% medium, 40% hard, 20% expert
- In-depth evaluation
- Full multi-dimensional analysis

---

## Data Flow

```
1. User Input → ADK Web UI
2. Web UI → Session Service (state management)
3. Session → root_agent
4. root_agent → Specialist Sub-Agent(s)
5. Sub-Agent → Gemini API (if needed)
6. Sub-Agent → root_agent (response)
7. root_agent → Session Service
8. Session → Web UI → User
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
| Deployment | Cloud Run | Latest |

---

## Design Patterns

### 1. Multi-Agent Orchestration
Follows ADK sub_agents pattern for specialized task routing.

### 2. Separation of Concerns
Each agent has single responsibility (SOLID principles).

### 3. Built-in Tool Integration
coding_agent uses BuiltInCodeExecutor (resolves ADK limitation).

### 4. Nested Multi-Agent
scoring_coordinator has 3 sub-agents for parallel evaluation.

### 5. Mode-Based Behavior
Difficulty modes adjust question complexity dynamically.

---

## Security Considerations

1. **Sandboxed Code Execution** - BuiltInCodeExecutor provides isolation
2. **Content Moderation** - safety_agent monitors all interactions
3. **No Hardcoded Secrets** - Environment variable configuration
4. **PII Detection** - Automated screening in safety_agent
5. **Input Validation** - All tools validate inputs

---

## Performance

- **Response Time:** <2s average (Gemini 2.5 Flash-Lite)
- **Concurrency:** Managed by ADK session service
- **Scaling:** Horizontal via Cloud Run
- **State:** Persistent across session

---

## Version History

- **v4.5** - Critic agent integration
- **v4.4** - Difficulty modes (Quick/Standard/Deep)
- **v4.3** - Multi-agent scoring system
- **v4.2** - Guided learning mode
- **v4.1** - Multi-agent architecture base
- **v4.0** - Initial ADK migration

---

## Future Enhancements

- File Search / Resume RAG (Vertex AI)
- Voice Interview (Gemini Live)
- Visual System Design (Diagrams)
- Multi-language Support

---

**For implementation details, see source code in `src/adk_interviewer/`**
