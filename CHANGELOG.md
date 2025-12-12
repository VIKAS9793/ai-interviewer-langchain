# Changelog

All notable changes to this project will be documented in this file.

## [v3.0.0] - 2025-12-12 (The Cognitive Upgrade)
### Added
- **Cognitive Engine:** Implemented "Autonomous Reasoning" with Chain-of-Thought (CoT).
- **RAG (Knowledge Grounding):** Integrated ChromaDB to verify answers against technical documentation.
- **Reflexion Agent:** Self-critique loop to improve question quality before asking.
- **Dynamic State Machine:** LLM-driven flow control with "Privacy Guardrails" (Support/Challenge modes).
- **Intrinsic Learning:** System now "learns" from successful interviews using `ReasoningBank`.
- **SessionManager:** Extracted state management service.
- **Micro-Service Architecture:** Refactored Monolith into `rag_service`, `critic_service`, `learning_service`.

### Changed
- **Major Refactor:** Decomposed `AutonomousInterviewer` into modular services.

### Planned
- **v3.1:** Gemini 2.5 Integration (Multi-modal native).

## [v2.6.0] - 2025-12-12

### 🎨 UI Overhaul (Major Refactor)
*   **Dark Mode Migration:** Switched from `gr.themes.Soft` to `gr.themes.Base` with custom slate palette.
*   **High Contrast:** Enforced WCAG-compliant text visibility across all components.
*   **Pill-Shaped Buttons:** Modernized button styling with rounded corners and proper spacing.
*   **Compact Layout:** Improved header and footer density for better information density.
*   **File Upload Styling:** Custom CSS to fix visibility issues in dark mode dropzones.

### 🐛 Bug Fixes & Stability
*   **Fixed Runtime Error:** Resolved `neutral_50` invalid theme variable crash.
*   **Fixed Dependency Error:** Added `libmagic1` and `python-magic` to resolve Practice Mode crash.
*   **Fixed Upload Visibility:** Force-styled file upload component to be visible in dark mode.
*   **Updated Disclaimer:** Clarified evaluation limitations in Practice Mode.

---

## [2.5.1] - 2025-12-11

### 🔥 Hotfix Release
*   **Downgraded Gradio to 4.44.0:** Resolved critical `TypeError: argument of type 'bool' is not iterable` caused by Gradio 5 schema parsing bug.
*   **Downgraded Torch to 2.3.1:** Resolved dependency conflict between `torch 2.5.1` (requires Triton 3.1) and `openai-whisper` (requires Triton < 3).
*   **Patched `main.py`:** Refactored boolean return values to explicit `gr.update()` objects for compatibility.

---

## [2.5.0] - 2025-12-11

### 🎯 Practice Mode (Resume-Based Interviews)
*   **Resume Upload:** PDF/DOCX support with security scanning (magic bytes, macro detection)
*   **Job Description URL Scraping:** Paste job link to extract JD context
*   **Intelligent Resume Analysis:** 40+ skills detection, role extraction, experience level parsing
*   **Role Detection:** Automatic detection of Business Development, PM, SWE, Data Science roles
*   **Experience Level:** Parses "X+ years" from resume (Junior/Mid/Senior)

### 🐛 Bug Fixes (9 Total)
*   **Fixed:** `custom_context` parameter missing from FlowController
*   **Fixed:** Button showing "True" after click (gr.update pattern)
*   **Fixed:** Skills key mismatch (`found_skills` vs `skills`)
*   **Fixed:** `InterviewSession` missing `metadata` field  
*   **Fixed:** Gradio 5 temp file path access errors
*   **Fixed:** Session stored as string instead of dict (string indices error)
*   **Fixed:** False positive skill matches (word boundary regex)
*   **Fixed:** Pydantic 2.11+ incompatibility (pinned to 2.10.6)
*   **Fixed:** Gradio cache directory for HuggingFace Spaces

### ⚠️ Known Limitations
*   Evaluation scoring optimized for technical interviews (Business/PM improvements in v3.0)
*   Gemini integration planned for v3.0

### 🎨 UI Improvements
*   **Full Width Layout:** `fill_width=True` for better screen utilization
*   **Tab Visibility Control:** Tabs hidden during active interview (in progress)

### 🛠️ Code Quality
*   **Extracted Helper Methods:** `_buttons_enabled()` and `_buttons_disabled()` reduce duplicate code
*   **Replaced 7 duplicate patterns** with helper method calls

### 🔒 Security & Stability
*   **Fixed bare `except:` clause** in FlowController (now logs errors)
*   **Added file error handling** in MetacognitiveSystem (IOError/OSError)

---

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
