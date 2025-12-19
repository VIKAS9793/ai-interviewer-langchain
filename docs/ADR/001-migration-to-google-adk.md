# ADR-001: Migration from LangGraph to Google ADK

**Status:** Accepted  
**Date:** December 19, 2025  
**Authors:** Vikas Sahani

---

## Context

The AI Technical Interviewer was originally built using:
- **LangChain/LangGraph** for agent orchestration
- **Gradio** for web interface
- **HuggingFace Spaces** for deployment

While functional, this architecture presented challenges:
1. Complex state management with SqliteSaver
2. Multiple abstraction layers (LangChain → Gemini)
3. Token exhaustion issues under load
4. Maintenance overhead of custom UI

---

## Decision

**Migrate to Google Agent Development Kit (ADK)** for a 100% Google-native stack.

### New Architecture
- **Framework:** Google ADK
- **LLM:** Gemini 2.5 Flash-Lite (native)
- **UI:** ADK Web (built-in)
- **Deployment:** Google Cloud Run (Free Tier)
- **State:** ADK SessionService with ToolContext

---

## Rationale

### Why Google ADK?

| Reason | Benefit |
|--------|---------|
| **Native Gemini Integration** | Direct API calls, no wrapper overhead |
| **Built-in Session Management** | No custom persistence code |
| **Multi-Agent Support** | SequentialAgent, ParallelAgent, LoopAgent |
| **Safety Guardrails** | Google's content filtering out-of-box |
| **Simpler Architecture** | 95% code reduction (20,862 deletions) |
| **Future-Proof** | Google-backed, actively developed |

### Considered Alternatives

1. **Keep LangGraph** - Rejected: Too complex for our needs
2. **Use LlamaIndex** - Rejected: Not Google-native
3. **Build Custom** - Rejected: Reinventing the wheel

---

## Consequences

### What We Gained ✅

1. **95% Code Reduction** - 20,862 deletions
2. **Native Performance** - Direct Gemini calls
3. **Built-in UI** - No Gradio maintenance
4. **Stateful Tools** - ToolContext state management
5. **Safety** - Google's guardrails
6. **Free Deployment** - GCP Free Tier

### Tradeoffs Made ⚠️

1. **Lost HuggingFace Visibility** - Less community exposure
2. **Gradio Customization** - ADK UI less customizable
3. **GCP Dependency** - Requires Google Cloud account
4. **ADK Maturity** - Still v1.x, may have breaking changes

### Migration Path

1. Created `google-adk` branch
2. Implemented ADK agents with ToolContext
3. Tested with Gemini API
4. Completed architectural audit
5 Remediated all HIGH/MEDIUM findings
6. Deprecated HuggingFace version
7. Updated documentation

---

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Gemini API](https://ai.google.dev/)
- [Cloud Run](https://cloud.google.com/run)

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-18 | Initial ADR created |
| 2025-12-19 | Migration completed |
| 2025-12-19 | Audit remediation complete (Phase 0 + Phase 1) |


---

## Context

The AI Technical Interviewer was originally built using:
- **LangChain/LangGraph** for agent orchestration
- **Gradio** for web interface
- **HuggingFace Spaces** for deployment

While functional, this architecture presented challenges:
1. Complex state management with SqliteSaver
2. Multiple abstraction layers (LangChain → Gemini)
3. Token exhaustion issues under load
4. Maintenance overhead of custom UI

---

## Decision

**Migrate to Google Agent Development Kit (ADK)** for a 100% Google-native stack.

### New Architecture
- **Framework:** Google ADK
- **LLM:** Gemini 2.5 Flash-Lite (native)
- **UI:** ADK Web (built-in)
- **Deployment:** Google Cloud Run (Free Tier)
- **State:** ADK SessionService

---

## Rationale

### Why Google ADK?

| Reason | Benefit |
|--------|---------|
| **Native Gemini Integration** | Direct API calls, no wrapper overhead |
| **Built-in Session Management** | No custom persistence code |
| **Multi-Agent Support** | SequentialAgent, ParallelAgent, LoopAgent |
| **Safety Guardrails** | Google's content filtering out-of-box |
| **Simpler Architecture** | 50% less code |
| **Future-Proof** | Google-backed, actively developed |

### Considered Alternatives

1. **Keep LangGraph** - Rejected: Too complex for our needs
2. **Use LlamaIndex** - Rejected: Not Google-native
3. **Build Custom** - Rejected: Reinventing the wheel

---

## Consequences

### What We Gained ✅

1. **50% Code Reduction** - Simpler codebase
2. **Native Performance** - Direct Gemini calls
3. **Built-in UI** - No Gradio maintenance
4. **Session Management** - Out of the box
5. **Safety** - Google's guardrails
6. **Free Deployment** - GCP Free Tier

### Tradeoffs Made ⚠️

1. **Lost HuggingFace Visibility** - Less community exposure
2. **Gradio Customization** - ADK UI less customizable
3. **GCP Dependency** - Requires Google Cloud account
4. **ADK Maturity** - Still v1.x, may have breaking changes

### Migration Path

1. Created `google-adk` branch
2. Implemented ADK agents
3. Tested with Gemini API
4. Deprecated HuggingFace version
5. Updated documentation

---

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Gemini API](https://ai.google.dev/)
- [Cloud Run](https://cloud.google.com/run)

---

## Changelog

| Date | Change |
|------|--------|
| 2025-12-18 | Initial ADR created |
| 2025-12-18 | Migration completed |
