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
