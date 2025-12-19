# ADK Interviewer – Architecture & Best‑Practices Audit Report

**Repository:** `VIKAS9793/ai-interviewer-google-adk` (Google ADK migration, v4.x)

**Audit date:** 2025-12-19

## 1) Goals & scope

### Goals
- Establish a **source-of-truth architecture map** (entry points, agents, tools, workflows, configuration, deployment).
- Research **official Google ADK best practices** for agentic architecture.
- Compare best practices vs current implementation and produce an **actionable remediation plan**.

### In scope
- ADK entry points (`root_agent` discovery), project structure, and runtime execution.
- Tool design (schemas, type hints, `ToolContext`, state usage).
- State/session management patterns.
- Multi-agent/workflow patterns (`SequentialAgent`, `LoopAgent`, `sub_agents`).
- Deployment patterns (local `adk web`, Cloud Run).

### Out of scope
- Deep model prompt quality evaluation.
- Product feature roadmap beyond architecture + best practices.

---

## 2) Official ADK references used

### Documentation
- **Agents overview (LLM/Workflow/Custom agents)**
  - https://google.github.io/adk-docs/agents/
- **Workflow agent best practices (SequentialAgent shared InvocationContext / state)**
  - https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/
- **Agent Config (root_agent.yaml / config-based agents)**
  - https://google.github.io/adk-docs/agents/config/
- **Tools & custom function tools (`ToolContext`, tool function conventions)**
  - https://google.github.io/adk-docs/tools-custom/
  - https://google.github.io/adk-docs/tools/
- **Sessions / state design & prefixes (`temp:`, `user:`, `app:`) and state mutation warnings**
  - https://google.github.io/adk-docs/sessions/state/
- **Context best practices (use most specific context; artifacts; tracked changes)**
  - https://google.github.io/adk-docs/context/
- **Cloud Run deployment notes (UI packaging / `--with_ui`)**
  - https://google.github.io/adk-docs/deploy/cloud-run/

### Official GitHub repos
- **ADK Python (core framework)**
  - https://github.com/google/adk-python
- **ADK Samples (reference implementations)**
  - https://github.com/google/adk-samples
- **ADK Web UI** (referenced from ADK Python README)
  - https://github.com/google/adk-web

---

## 3) Current codebase architecture map

### Top-level
- `requirements.txt` – minimal dependencies: `google-adk`, `python-dotenv`.
- `.env.example` – env var template (`GOOGLE_API_KEY`, `LOG_LEVEL`, etc.).
- `Dockerfile` – runs `adk web` in container.
- `cloudrun-service.yaml` – Cloud Run service config.
- `deploy-cloudrun.sh` – helper script (currently inconsistent; see findings).
- `docs/*` – architecture/deployment/setup/ADR.

### Python package
`src/adk_interviewer/`
- `agent.py`
  - Defines a `root_agent` **self-contained**, `tools=[]`.
- `main.py`
  - Loads `.env` via `python-dotenv`, configures logging, imports `root_agent` from `agents/interviewer_agent.py`, validates config.
- `config/settings.py`
  - `ADKConfig` dataclass and `validate_config()` (requires `GOOGLE_API_KEY`).
- `agents/`
  - `interviewer_agent.py` – defines a tool-augmented interviewer agent and a `root_agent`.
  - `critic_agent.py` – defines `create_critic_agent()`.
  - `safety_agent.py` – defines `create_safety_agent()`.
- `tools/`
  - `question_generator.py` – `generate_question()`.
  - `answer_evaluator.py` – `evaluate_answer()`.
  - `resume_parser.py` – `parse_resume()`.
  - `jd_analyzer.py` – `analyze_job_description()`.
- `workflows/interview_flow.py`
  - Defines a `SequentialAgent` / `LoopAgent` interview workflow.

### Runtime models (what likely runs today)
This repo currently has **multiple competing “root agent” definitions**:
- `src/adk_interviewer/agent.py: root_agent` (no tools)
- `src/adk_interviewer/agents/interviewer_agent.py: root_agent` (tools enabled)
- `src/adk_interviewer/main.py` exports `root_agent` from `agents/interviewer_agent.py`

Which agent ADK loads depends on **how `adk web` is invoked** (source-dir vs module path) and ADK’s discovery rules.

---

## 4) ADK best practices (condensed)

### 4.1 Choose correct agent types
From ADK docs:
- Use **LLM agents** (`Agent`, `LlmAgent`) for language-heavy reasoning and tool selection.
- Use **Workflow agents** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) for deterministic orchestration.
- Use **Custom agents** (`BaseAgent`) when predefined patterns are insufficient.

### 4.2 Multi-agent orchestration & state handoff
- `SequentialAgent` is deterministic; it runs sub-agents in order.
- Sub-agents share the same **InvocationContext**, including `ctx.session.state` and the **`temp:` namespace**, enabling safe step-to-step handoff.

### 4.3 Tool best practices (function tools)
From ADK tools docs:
- Tool functions should have:
  - **Clear verb-noun names**.
  - **Strong type hints** for all parameters.
  - **JSON-serializable** parameter types.
  - **No default values** for parameters (models don’t reliably use defaults).
- Return values should be a `dict` (or will be wrapped).
- For advanced scenarios, use `tool_context: ToolContext` to:
  - update tracked/persisted state via `tool_context.state`,
  - control flow via `tool_context.actions`.
- Do **not** mention `tool_context` in the tool docstring (it’s injected by ADK).

### 4.4 State / session best practices
From ADK state docs:
- Use state prefixes intentionally:
  - `temp:` for per-invocation scratchpad
  - `user:` for per-user preferences
  - `app:` for app-wide shared values
  - no prefix for per-session state
- Avoid direct state mutation on sessions retrieved directly from a SessionService **outside** tool/callback contexts.

### 4.5 Context best practices
- Use the **most specific context** available:
  - `ToolContext` in tools
  - `CallbackContext` in callbacks
  - `InvocationContext` in agent core logic only when necessary
- Prefer **artifacts** for file/blob references (`context.save_artifact`/`load_artifact`), store references in state.

### 4.6 Deployment best practices (Cloud Run)
- ADK Cloud Run deployment docs highlight that UI assets are not included by default unless configured (e.g., `adk deploy cloud_run --with_ui`).
- Cloud Run sets `PORT`; processes should respect it.

---

## 5) Gap analysis: Best practices vs current implementation

### 5.1 Entry points & agent discovery
**Finding A1 (HIGH): Conflicting entry points / multiple `root_agent` definitions**
- Evidence:
  - `src/adk_interviewer/agent.py` defines `root_agent` (no tools).
  - `src/adk_interviewer/agents/interviewer_agent.py` defines `root_agent` (tools enabled).
  - `src/adk_interviewer/main.py` exports `root_agent` from `agents/interviewer_agent.py`.
- Risk:
  - Different runtime behavior depending on how ADK loads the agent.
  - Increased onboarding friction and “it works locally but not on Cloud Run” class bugs.
- ADK best practice alignment:
  - ADK examples in `google/adk-python` show a single, canonical `root_agent` definition.

**Recommendation:** choose exactly one canonical ADK entrypoint strategy.
- Option 1 (code-first): keep a single `agent.py` exporting `root_agent` and ensure docs/Docker use that.
- Option 2 (package module): export `root_agent` from one place and remove/rename the others.

---

### 5.2 Code correctness
**Finding A2 (HIGH): `agents/interviewer_agent.py` references `config` without importing it**
- Evidence:
  - In `create_interviewer_agent()`: `model=model or config.MODEL_NAME`, but `config` is not imported.
- Risk:
  - Runtime `NameError` when this module’s factory is used.

**Recommendation:** import `config` explicitly (and add a minimal smoke test / `adk run` check in CI).

---

### 5.3 Workflow architecture (Sequential/Loop)
**Finding A3 (MEDIUM): Workflow code exists but is not wired into execution**
- Evidence:
  - `workflows/interview_flow.py` defines `create_interview_workflow()` but no entrypoint uses it.
- Risk:
  - Dead code and mismatched mental model (“we have multi-agent flow”) vs actual runtime (“single LLM agent”).

**Recommendation:** either:
- integrate the workflow as the canonical `root_agent`, or
- remove/park it behind a feature flag to reduce confusion.

**Finding A4 (MEDIUM): `workflows/interview_flow.py` imports factories from `..agents` that are not exported**
- Evidence:
  - `from ..agents import create_interviewer_agent, create_critic_agent, create_safety_agent`
  - but `agents/__init__.py` does not export those functions.
- Risk:
  - Import errors if workflow is used.

---

### 5.4 Tools vs ADK tool best practices
**Finding T1 (MEDIUM): Tool functions define default values for parameters**
- Evidence:
  - `generate_question(difficulty: str = "medium", previous_questions: Optional[list[str]] = None, ...)`
  - `evaluate_answer(... topic: str = "", difficulty: str = "medium")`
- Why it matters:
  - ADK docs caution that default values are not reliably supported/used by models during tool call generation.

**Recommendation:** remove defaults for tool params that the model is expected to provide, or ensure instructions guarantee the model always supplies required args.

**Finding T2 (MEDIUM): Tools are not using `ToolContext` / session state, limiting “adaptivity”**
- Evidence:
  - Tools are stateless and do not read/write `session.state`.
- Risk:
  - Interview adaptivity across turns is limited unless the LLM alone maintains context.

**Recommendation:**
- Store structured interview state in `session.state` (e.g., `asked_questions`, `topic`, `scores`, `difficulty_level`).
- Use `temp:` for per-invocation intermediates.

**Finding T3 (LOW): Some tool parameter typing is broad**
- Evidence:
  - `candidate_context: Optional[dict]` (untyped dict) in `generate_question()`.
- Recommendation:
  - Use `dict[str, Any]` and document expected keys, or a typed schema object.

---

### 5.5 State/session management
**Finding S1 (LOW): Config suggests stateful design but runtime does not implement it**
- Evidence:
  - `ADKConfig` includes session limits/timeouts, safety flags, etc.
  - No code applies these values to a SessionService or enforcement layer.

**Recommendation:**
- Either implement these knobs (SessionService choice, concurrency controls) or remove unused config to keep the system honest.

---

### 5.6 Safety architecture
**Finding G1 (MEDIUM): Safety/Critic agents exist but are not part of the orchestration**
- Evidence:
  - `agents/safety_agent.py` and `agents/critic_agent.py` exist.
  - No runtime composition shows them being invoked.
- Risk:
  - Documented safety posture may not match real behavior.

**Recommendation:**
- If using multi-agent workflow, run `question_generator` → `critic` → `interviewer`.
- Or, keep single agent but add explicit “safety checks” prompts and/or tool-driven sanitization.

---

### 5.7 Deployment
**Finding D1 (HIGH): `deploy-cloudrun.sh` references a non-existent Dockerfile**
- Evidence:
  - Script uses `docker build -f Dockerfile.adk ...` but repo has `Dockerfile`.
- Risk:
  - Deployment automation breaks.

**Recommendation:**
- Fix script to reference `Dockerfile` or add the missing file.

**Finding D2 (INFO): Cloud Run UI packaging considerations**
- Evidence:
  - Official docs warn UI not included by default in ADK deploy flows unless `--with_ui`.
  - This repo uses custom Docker that runs `adk web`, which should include UI in the container.

**Recommendation:**
- Document explicitly that the project uses **custom Docker-based Cloud Run deployment**, not `adk deploy cloud_run`.

---

## 6) Recommended target architecture (aligned to ADK best practices)

### Option A (recommended): Deterministic workflow + tool/state
Use `workflows/interview_flow.py` (or a custom `BaseAgent`) as the canonical `root_agent`.
- `SequentialAgent` high-level pipeline:
  1. Greeter
  2. Loop: question generation (tool or LLM) → critic/safety screen → ask → evaluate
  3. Reporter
- Store interview progress in `session.state`:
  - `topic`, `asked_questions`, `question_index`, `scores`, `difficulty`.

### Option B: Single LLM agent with tools
Keep one `Agent` as `root_agent`, but:
- Use tools with stricter ADK conventions (no defaults; typed params).
- Persist structured state in `ToolContext.state`.

### Option C: Agent Config YAML
If you want best-in-class portability and alignment with ADK config tooling:
- Add `root_agent.yaml` and use `adk create --type=config` patterns.
- Use config-defined `sub_agents` and `tools`.

---

## 7) Prioritized remediation plan

### Phase 0: Fix correctness & consistency (1–2 hours)
- Resolve the `config` import bug in `agents/interviewer_agent.py`.
- Choose the canonical `root_agent` export and remove ambiguity.
- Fix `deploy-cloudrun.sh` Dockerfile reference.

### Phase 1: Align with ADK patterns (0.5–2 days)
- Wire in workflow orchestration OR remove workflows to reduce dead code.
- Refactor tools to match ADK guidance (remove defaults, improve typing).
- Introduce session state tracking (`asked_questions`, `scores`, etc.) using `ToolContext.state`.

### Phase 2: Hardening (2–5 days)
- Add minimal CI checks:
  - import/smoke test
  - `adk run` happy path
- Add evaluation harness using `adk eval` (see `adk-python` README).

---

## 8) Appendix: Quick “what runs where” checklist

- Local dev recommended command (docs): `adk web src`
- Docker prod command: `adk web --port 8080 --host 0.0.0.0 adk_interviewer`
- Ensure both commands load the **same** `root_agent` implementation.

---

## 9) Summary

This codebase is a solid scaffold for an ADK-based interviewer, but it currently diverges from ADK best practices in ways that can cause inconsistent runtime behavior:
- Multiple competing `root_agent` definitions.
- At least one correctness bug (`config` not imported).
- Workflow/safety/critic architecture exists but is not integrated.
- Tools are not yet designed around ADK’s `ToolContext`/state patterns.

Addressing the **HIGH severity items** will significantly improve reliability and make the project align with official ADK patterns and sample architectures.
