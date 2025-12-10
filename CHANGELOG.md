# Changelog

All notable changes to this project will be documented in this file.

## [2.4.0] - 2025-12-10

### 🎤 Voice Mode (Browser-Native)
*   **Speech-to-Text:** Browser `webkitSpeechRecognition` for hands-free input
*   **Text-to-Speech:** Browser `speechSynthesis` for AI response playback
*   **Zero External API Calls:** All voice processing in-browser (zero cost)
*   **Security:** Input sanitization, rate limiting (3s cooldown), XSS prevention

---

## [2.3.1] - 2025-12-10

### 🛡️ Stability Patch
*   **Single-Model Architecture:** Consolidated all LLM calls to `meta-llama/Meta-Llama-3-8B-Instruct`
*   **Removed Qwen/Mistral References:** Eliminated "Task not supported" API errors
*   **Fixed NameError:** Resolved circular import in Config default arguments
*   **UI Model Selector Removed:** Prevents user confusion with fixed architecture
*   **Code Evaluation Rolled Back:** Disabled due to Free Tier API limitations

---

## [2.2.2] - 2025-12-08

### 🧹 Codebase Cleanup
*   Removed all Ollama/local-first references
*   Updated all documentation for cloud-first architecture
*   Standardized model references to HuggingFace IDs

---

## [2.2.1] - 2025-12-08

### 🎯 Hybrid Evaluation Strategy
*   **Dual-Model Architecture:** LLaMA-3 for questions, Qwen2.5-32B for evaluation
*   **Prometheus-Style Rubrics:** 1-5 scoring scale with explicit criteria
*   **Rebalanced Weights:** 60% LLM / 40% Heuristic merge
*   **Depth Bonus:** Extra points for comprehensive 150+ word structured answers

---

## [2.2.0] - 2025-12-08

### ✨ Enhanced Evaluation
*   **AI Internal Monologue:** Collapsible display of reasoning chain
*   **Knowledge Grounding:** Answer verification against authoritative sources
*   **Semantic Relevance Checking:** Embedding-based off-topic detection
*   **Semantic Caching:** LRU caches for embeddings and similarity scores

---

## [2.1.0] - 2025-12-07

### ☁️ Cloud-First Deployment
*   HuggingFace Spaces deployment
*   HuggingFace Inference API integration
*   Multi-model support (LLaMA, Mistral, Qwen)
*   Gradio UI with progress tracking

---

## [2.0.0] - 2025-12-07

### 🚀 Major Release: Autonomous Agent Architecture

This release marks a fundamental shift from a simple LLM wrapper to a true **Autonomous Agent**.

### ✨ New Features
*   **ReasoningBank (Memory System):** Persistent memory for learning strategies
*   **ReflectAgent (Critic):** Self-reflection loop for fairness evaluation
*   **Metacognitive System:** Self-assessment and proficiency tracking
*   **AI Guardrails:** Responsible AI with bias detection

### 🛠️ Improvements
*   Clean `src/` modular structure
*   Centralized `data/memory/` storage
*   Pinned dependencies for stability
