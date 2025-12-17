# LangGraph Interview Flow Architecture

This document visualizes the internal state machine powering the AI Interviewer's brain.

## Interview Graph (Stateful Loop)

```mermaid
stateDiagram-v2
    [*] --> check_resume: START
    
    check_resume --> extract_context: New Session (Q=0)
    check_resume --> evaluate: Answer Received (Q>0 + Answer)
    check_resume --> generate_question: Resume (Q>0, No Answer)
    
    extract_context --> generate_greeting: Context Extracted
    generate_greeting --> generate_question: Greeting Generated
    
    generate_question --> validate_question: Question Generated
    validate_question --> await_answer: Question Validated
    
    await_answer --> [*]: INTERRUPT (Wait for User)
    
    note right of await_answer
        Graph pauses here.
        User submits answer.
        Graph resumes via invoke().
    end note
    
    await_answer --> evaluate: Answer Submitted
    evaluate --> decide: Evaluation Complete
    
    decide --> generate_question: Continue (Q < Max)
    decide --> report: Complete (Q >= Max)
    
    report --> [*]: END
```

## Node Responsibilities

| Node | Purpose | Output Keys |
|------|---------|-------------|
| `check_resume` | Route entry point | `session_id` |
| `extract_context` | Parse resume/JD | `target_role`, `phase` |
| `generate_greeting` | Personalized intro | `greeting`, `question_number` |
| `generate_question` | LLM question gen | `current_question`, `question_number` |
| `generate_question` | LLM question gen (TTD) | `current_question`, `question_number` |
| `validate_question` | Final sanity check | `current_question` |
| `await_answer` | Interrupt point | `current_answer` |
| `evaluate` | Prometheus scoring | `qa_pairs`, `performance_history` |
| `decide` | Continue/Complete | `is_complete` |
| `report` | Final summary | `final_report` |

## Conditional Routing Logic

```mermaid
flowchart TD
    subgraph EntryRouter["_determine_entry_point"]
        A{Question Number?}
        A -->|Q = 0| B[New Session]
        A -->|Q > 0| C{Has Answer?}
        C -->|Yes| D[Evaluate Answer]
        C -->|No| E[Resume Question]
    end
    
    subgraph ContinueDecision["_should_continue"]
        F{Q < Max?}
        F -->|Yes| G[Generate Next Q]
        F -->|No| H[Generate Report]
    end
```

## State Schema (InterviewState)

```python
class InterviewState(TypedDict):
    session_id: str
    candidate_name: str
    topic: str
    target_role: Optional[str]
    company_name: Optional[str]
    resume_skills: List[str]
    jd_requirements: List[str]
    experience_years: int
    question_number: int
    max_questions: int
    current_question: Optional[str]
    current_answer: Optional[str]
    qa_pairs: List[Dict[str, Any]]
    performance_history: List[int]
    candidate_state: str
    phase: str
    is_complete: bool
    greeting: Optional[str]
    final_report: Optional[Dict[str, Any]]
    messages: Annotated[list, add_messages]
```

---

*This diagram reflects the actual implementation in `src/ai_interviewer/core/interview_graph.py`.*

**Persistence:** State is checkpointed via `SqliteSaver` to `interview_state.sqlite` (configurable via `INTERVIEW_DB_PATH` env var).
