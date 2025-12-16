# Changelog

All notable changes to this project will be documented in this file.

## [v3.3.0] - 2025-12-16 (Semantic & TTD Intelligence)

### 🧠 Time Test Diffusion (TTD)
- **Deep Research Algorithm:** Implemented iteratively refining question generator (Fareed Khan's architecture)
- **Red Team Agent:** Adversarial critique for every question (checks bias, clarity, off-topic)
- **Question Evaluator:** Programmatic scoring (0-10) for relevance and depth
- **Denoising Loop:** Self-corrects questions until quality threshold is met

### 🛡️ Semantic Deduplication
- **Zero Duplicates:** Replaced substring matching with `sentence-transformers` (all-MiniLM-L6-v2)
- **Cosine Similarity:** Similarity threshold >= 0.70 flags as duplicate
- **Dual-Layer Protection:** Checks in `SemanticDeduplicator` module + `CriticService`

### ⚖️ Global Rate Limiting
- **Quota System:** Enforced 1 interview/day limit per system
- **Reset Logic:** Auto-resets at midnight UTC
- **User Notification:** Clear UI blocking when quota exhausted

### 🧪 Robustness
- **Rigorous Testing:** 113 tests passing (100% coverage of core paths)
- **Mocking Strategy:** Improved integration tests for flakiness prevention

---

## [v3.2.3] - 2025-12-14 (Type Safety & Code Quality)

### 🔍 Type Checking & Code Quality
- **Mypy Integration:** Added comprehensive static type checking with `mypy`
  - Configured `mypy.ini` with strict type checking settings
  - Fixed all 46+ type errors across 19 files
  - Added type annotations throughout the codebase
- **Type Safety Improvements:**
  - Added `TypedDict` models for better type safety (`src/ai_interviewer/utils/types.py`)
  - Fixed Optional type annotations (no implicit Optional)
  - Added proper return type annotations with `cast()` for LLM responses
  - Fixed union type issues in controller and flow controllers
- **Import Handling:**
  - Configured mypy to ignore missing imports for optional dependencies
  - Added `pyright: ignore` comments for IDE compatibility (basedpyright)
  - Proper handling of optional imports (whisper, langchain modules)

### 🔧 Technical Changes
- **Added:** `mypy.ini` - Mypy configuration file
- **Modified:** All core modules with proper type annotations
  - `controller.py` - Fixed flow controller types, whisper model checks
  - `autonomous_reasoning_engine.py` - Fixed return types, Optional annotations
  - `autonomous_interviewer.py` - Fixed return type annotations
  - `ui/app.py` - Fixed tuple vs dict type mismatches
  - `ui/interfaces.py` - Updated protocol to match implementation
  - `resume_parser.py` - Cleaned up type ignore comments
  - `critic_service.py` - Fixed dict type annotations
  - `knowledge_store.py` - Removed unused type ignores
  - And 10+ other files

### 📚 Documentation
- **Updated:** `docs/CONTRIBUTING.md` - Added type checking guidelines
- **Updated:** `docs/SETUP.md` - Added mypy installation and usage instructions

### ✅ Quality Metrics
- **Type Coverage:** 100% of core modules now have proper type annotations
- **Mypy Status:** `Success: no issues found in 37 source files`
- **Code Quality:** Improved IDE support and catch errors at development time

---

## [v3.2.2] - 2025-12-14 (Security Hardening)

### 🔒 Security Enhancements
- **SSRF Protection:** Added URL validation to prevent Server-Side Request Forgery attacks
  - Blocks localhost, private IPs, and dangerous URL schemes
  - Multi-layer validation (URL parsing + IP checking + scheme validation)
- **Input Validation:** Comprehensive validation for all user inputs
  - New `InputValidator` class with OWASP-compliant validation rules
  - Validates name, answers, URLs, and voice transcripts
  - XSS pattern detection and control character filtering
- **Session Expiration:** Automatic session cleanup with activity-based expiration
  - 1 hour default expiration time
  - Background cleanup thread runs every 5 minutes
  - Thread-safe operations with locking mechanism
- **Error Sanitization:** Environment-aware error messages
  - Generic messages in production (prevents information disclosure)
  - Detailed messages in development (aids debugging)
- **Input Length Limits:** Protection against memory exhaustion
  - Name: 100 characters max
  - Answer: 5000 characters max
  - Job Description: 10000 characters max
  - Voice Transcript: 2000 characters max

### 🧪 Testing
- **Security Test Suite:** Added comprehensive tests for all security fixes (`tests/test_security_fixes.py`)
  - 25 security tests covering all implemented fixes
  - 100% pass rate (25/25 tests passed)
  - Fast execution time (6.88s)
- **Coverage:** Input validation, SSRF protection, session expiration, error sanitization

### 📚 Documentation
- **Audit Report:** Complete security audit findings (`docs/AUDIT_REPORT.md`)
- **Implementation Guide:** Detailed security implementation documentation (`docs/SECURITY_IMPLEMENTATION.md`)
- **Updated README:** Added security features section and documentation links
- **Updated Troubleshooting:** Added security & validation issues section
- **Updated Roadmap:** Added v3.2.2 security hardening completion status

### 🔧 Technical Changes
- **Added:** `src/ai_interviewer/utils/input_validator.py` - Centralized input validation module
- **Modified:** `src/ai_interviewer/utils/url_scraper.py` - Added SSRF protection
- **Modified:** `src/ai_interviewer/controller.py` - Integrated input validation and error sanitization
- **Modified:** `src/ai_interviewer/core/session_manager.py` - Added session expiration and cleanup
- **Modified:** `src/ai_interviewer/utils/config.py` - Added security constants

---

## [v3.2.1] - 2025-12-14 (Hybrid LLM + Architecture Alignment)

### 🔌 Hybrid LLM Support
- **OpenAI Integration:** Added `langchain-openai` for native structured output support
- **Provider Selection:** New `LLM_PROVIDER` config (openai/huggingface/hybrid)
- **Instructor Library:** Added for Pydantic-based structured output with any LLM

### 🎯 Resume Parsing Improvements
- **Pydantic Model:** Added `ResumeAnalysis` model for type-safe skill extraction
- **3-Tier Fallback:** Pydantic structured → JSON parsing → Heuristic keywords
- **Expanded Keywords:** Skill detection from 13 to 40+ (TypeScript, FastAPI, GCP, etc.)

### 💬 Feedback Improvements
- **LLM-Generated Feedback:** Replaced hardcoded "Strong answer!" templates
- **Personalized Strengths:** LLM analysis of actual answers for growth areas
- **Dynamic Confidence:** Removed hardcoded 70% placeholders where possible

### 📝 Documentation
- **Current Limitations:** Added user-friendly limitations section to README
- **Practice Mode Disclaimer:** Updated from negative "Limitation Note" to positive "What to Expect"
- **SETUP.md:** Added OpenAI API key configuration instructions

### 🐛 Bug Fixes
- Fixed `detected_skills` showing "Not detected" (wrong key: `found_skills` → `skills`)
- Fixed `InterviewGraph.analyze_resume()` hardcoded stub (now delegates to reasoning engine)
- Verified complete call chain: controller → interview_graph → interviewer → reasoning_engine

---

## [v3.2.0] - 2025-12-14 (Modular UI & Company Intelligence)

### 🏢 Company Intelligence
- **Strategy Injection:** Customized evaluation for Amazon (Leadership Principles), Google (GCA), and Meta (Move Fast).
- **Context Awareness:** JD analysis now triggers specific questioning strategies.

### 🏗️ Architecture Modularization
- **UI Refactoring:** Decoupled `controller.py` from Gradio dependencies.
- **Clean Architecture:** Moved all UI logic to `src/ui/`.
- **Adapter Pattern:** Implemented `InterviewHandlers` to bridge Core and UI.
- **Micro-Components:** Refactored `feedback.py`, `inputs.py`, and `tabs/` modules.

---

## [v3.1.0] - 2025-12-12 (LangGraph + Intelligence Layer)

### 🔷 LangGraph Integration
- **State Machine:** Unified interview flow with 8 nodes (check_resume → generate_greeting → generate_question → validate_question → await_answer → evaluate → decide → generate_report)
- **Checkpointing:** Session persistence with `MemorySaver` for resume/recovery
- **Interrupts:** Human-in-the-loop support for answer submission

### 🎯 JD Parser & Role Detection
- **URL Scraping:** Extracts job description from URLs
- **Role Extraction:** Detects role title and company name from JD text/URL
- **Context-Aware Greetings:** Personalized greetings based on detected role and company

### 🧠 Smart Role Parsing
- **Core Role Detection:** Extracts primary role (e.g., "Product Manager" from "Senior Product Manager - YouTube")
- **Area Context:** Identifies specific area (e.g., "YouTube Channel Memberships")
- **Topic Mapping:** Maps roles to interview topics automatically

---

## [v3.0.1] - 2025-12-12 (Hotfix: Logic Bugs)

### 🐛 Bug Fixes
- Fixed scoring calculation (was using raw LLM score instead of merged score)
- Fixed question counter not incrementing properly
- Fixed feedback generation returning empty strings
- Fixed topic validation in practice mode

---

## [v3.0.0] - 2025-12-12 (The Cognitive Upgrade)

### 🧠 Micro-Services Architecture
- **Orchestrator:** `autonomous_interviewer.py` - Central coordination
- **State Layer:** `session_manager.py` - Thread-safe session management
- **RAG Service:** `rag_service.py` - Knowledge grounding with ChromaDB
- **Critic Service:** `critic_service.py` - Self-correction and quality control
- **Learning Service:** `learning_service.py` - ReasoningBank for pattern memory

### 🔄 Autonomous Reasoning
- **Chain-of-Thought:** Every decision preceded by reasoning process
- **Self-Reflection:** Metacognitive system for adaptive behavior
- **Reflexion Loop:** Critic Service validates questions before asking

### 📊 Evaluation System
- **Prometheus-Style Rubric:** 1-5 scale scoring
- **60/40 LLM/Heuristic Merge:** Balanced evaluation approach
- **Semantic Relevance:** Sentence Transformers for answer relevance checking

---

## [v2.6.0] - 2025-12-12 (UI Overhaul)

### 🎨 UI Improvements
- **Dark Mode:** Full dark theme support
- **Pill Buttons:** Modern button styling
- **High Contrast:** Improved accessibility
- **Progress Tracking:** Visual progress indicators

---

## [v2.5.1] - 2025-12-11 (Hotfix)

### 🐛 Bug Fixes
- Downgraded Gradio from 5.9.1 to 4.44.0 (schema parsing bug)
- Fixed Torch/Triton conflict
- Resolved dependency conflicts

---

## [v2.5.0] - 2025-12-11 (Practice Mode)

### 📄 Practice Mode Features
- **Resume Upload:** PDF/DOCX support with security scanning (magic bytes, macro detection)
- **JD URL Scraping:** Extract job description from URLs
- **Intelligent Resume Analysis:** 40+ skill detection, role detection, experience level
- **Context-Aware Questions:** Questions based on resume and JD

### 🔒 Security & Stability
- **File Validation:** Magic byte checking, size limits (10MB)
- **Threat Detection:** PDF JavaScript/auto-action detection, DOCX macro/OLE detection
- **Input Sanitization:** HTML sanitization, control character removal
- **Security:** Input sanitization, rate limiting (3s cooldown), XSS prevention

---

## [v2.4.0] - 2025-12-10 (Voice Mode)

### 🎤 Voice Features
- **Browser-Native STT:** WebKit Speech Recognition API
- **Browser-Native TTS:** Speech Synthesis API
- **Zero External APIs:** Fully client-side implementation
- **Rate Limiting:** 3-second cooldown between recordings

---

## [v2.3.1] - 2025-12-10 (System Stability)

### 🔧 Stability Improvements
- Enforced Single-Model Architecture (LLaMA 3)
- Removed all unstable multi-model code
- Dry codebase & cleanup

---

## [v2.2.2] - 2025-12-08 (Codebase Cleanup)

### 🧹 Cleanup
- Removed all legacy Ollama references
- Updated documentation for cloud-first
- Cleaned binary files from git history
- Optimized UI text for cloud

---

## [v2.2.1] - 2025-12-08 (Hybrid Evaluation)

### 📊 Evaluation Improvements
- Dual-model evaluation (Deprecated → Now Single-Model)
- Prometheus-style 1-5 rubric scoring
- 60/40 LLM/Heuristic merge weights
- Depth bonus for comprehensive answers

---

## [v2.2.0] - 2025-12-08 (Enhanced Evaluation)

### 🎯 Evaluation Features
- AI Internal Monologue display
- Knowledge Grounding verification
- Semantic Relevance Checking (Sentence Transformers)
- Semantic Caching (LRU)

---

## [v2.1.0] - 2025-12-07 (HuggingFace Spaces)

### ☁️ Cloud Deployment
- Cloud-first architecture with HF Inference API
- Multi-model support (Initial experiments)
- Gradio UI with progress tracking

---

## [v2.0.0] - 2025-12-07 (Autonomous Agent)

### 🤖 Autonomous Features
- Autonomous Reasoning Engine with Chain-of-Thought
- ReasoningBank (Memory) and ReflectAgent (Self-Correction)
- AI Guardrails for fair, unbiased evaluation
- Clean modular `src/` structure

