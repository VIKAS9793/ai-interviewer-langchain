# 📋 Architecture Decision Records (ADR)

> **Last Updated:** 2025-12-08

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

## 2. Dual-Model Evaluation Strategy

**Status:** Accepted

**Context:** LLaMA 3 (8B) is good for conversational question generation but tends to be conservative in scoring evaluations.

**Decision:** Use **two different models**:
- **LLaMA 3 (8B)** for question generation
- **Qwen2.5 (32B)** for answer evaluation

**Consequences:**
- ✅ Better calibrated scores
- ✅ Prometheus-style rubric compatibility
- ⚠️ Slightly higher latency (two model calls)

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
