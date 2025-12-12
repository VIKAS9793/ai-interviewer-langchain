# 📋 Architecture Decision Records (ADR)

> **Last Updated:** 2025-12-12

## 1. Cloud-First Deployment

**Status:** Accepted

**Context:** The project was originally designed for local execution with Ollama. However, HuggingFace Spaces provides free hosting with serverless GPU inference.

**Decision:** Adopt a **cloud-first architecture** using HuggingFace Inference API as the primary deployment target.

**Consequences:**
- ✅ No local GPU required
- ✅ Free hosting on HuggingFace Spaces
- ✅ Automatic scaling
- ⚠️ Requires internet connectivity
- ⚠️ Subject to API rate limits

---

## 2. Single-Model Evaluation Strategy (Architecture Simplified)
**Status:** Accepted (Replaces Dual-Model)
**Context:** Multi-model inference (Mistral/Qwen) on Free Tier caused 500 errors ("Task not supported").
**Decision:** Standardize on **Meta-LLaMA-3 (8B)** for BOTH generation and evaluation.
**Consequences:**
- ✅ 100% API Stability (No "Task not supported" errors)
- ✅ Simplified Architecture (DRY)
- ⚠️ Sacrifices nuanced scoring of larger models for reliability

---

## 3. 1-5 Scale Instead of 1-10

**Status:** Accepted

**Context:** Research (Prometheus, FARE) shows that 1-5 scales yield more reliable and consistent LLM evaluations.

**Decision:** Use **1-5 scoring scale** internally, convert to 1-10 for UI display.

**Consequences:**
- ✅ More consistent scores
- ✅ Easier rubric definitions
- ✅ Higher human correlation

---

## 4. Semantic Relevance Checking

**Status:** Accepted

**Context:** The AI was incorrectly scoring off-topic answers highly because heuristics only checked keywords.

**Decision:** Add **embedding-based semantic similarity** using Sentence Transformers.

**Consequences:**
- ✅ Detects off-topic answers accurately
- ✅ Cached embeddings for performance
- ⚠️ Additional dependency (sentence-transformers)

---

## 5. Micro-Kernel Architecture (v3.0)

**Status:** Accepted

**Context:** The `AutonomousInterviewer` class grew into a "God Class" (1200+ lines), making testing and maintenance difficult. File corruption issues highlighted the need for separation.

**Decision:** Refactor into a **Micro-Service Architecture**:
*   **Orchestrator:** `AutonomousInterviewer` (Stateless Controller).
*   **State:** `SessionManager` (Isolated Logic).
*   **Cognition:** `CognitiveModules` (RAG, Critic, Learner).

**Consequences:**
*   ✅ **Testability:** Can verify `rag_service` without mocking the whole app.
*   ✅ **Stability:** "God Class" corruption risk eliminated.
*   ✅ **Scalability:** Modules can eventually become separate API endpoints.

---

## 6. Docker-Based Deployment (v3.0)

**Status:** Accepted

**Context:** Hugging Face Spaces environment can vary. Relying on "standard" python environment led to inconsistencies.

**Decision:** Use **Docker** as the deployment standard.

**Consequences:**
*   ✅ **Reproducibility:** "Works on my machine" = Works on Cloud.
*   ✅ **Control:** We define the OS, User ID, and exact library versions.
*   ⚠️ **Build Time:** Slower deployment (must build container).

---

## 7. Intrinsic Learning (Skill Graph)

**Status:** Accepted

**Context:** The interviewer was static. It didn't "improve" after seeing good answers.

**Decision:** Implement `LearningService` that extracts "Winning Strategies" from successful interviews (Score > 8/10) and stores them in `ReasoningBank`.

**Consequences:**
*   ✅ **Adaptive:** System gets smarter over time.
*   ✅ **Data-Driven:** Rubrics evolve based on real candidate data.

