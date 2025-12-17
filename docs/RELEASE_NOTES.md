# 💾 AI Interviewer v3.3.1: Persistence & Cost Control

**Release Date:** December 17, 2025  
**Tag:** `v3.3.1`  
**Focus:** Durable State Persistence, LLM Cost Optimization, Smart Fallback.

---

## 🌟 Major Highlights

### 1. SQLite Persistence (True Memory)
- Replaced ephemeral `MemorySaver` with `SqliteSaver` for session state
- Sessions survive container restarts on HuggingFace Spaces
- Path configurable via `INTERVIEW_DB_PATH` env var (auto-creates directories)

### 2. Cost Control (75% Reduction)
- Reduced TTD loop from 3 iterations to 1 (`MAX_ITERATIONS=1`)
- Prevents token exhaustion on free-tier LLM APIs (Gemini Flash-Lite)

### 3. Smart Rotating Fallback
- 5 distinct fallback questions replace static template
- Fallback index rotates based on question number (no repetition)

---

# 🔒 AI Interviewer v3.2.2: Security Hardening

**Release Date:** December 14, 2025  
**Tag:** `v3.2.2`  
**Focus:** Enterprise-Grade Security Controls and Input Validation.

---

## 🌟 Major Highlights

### 1. Comprehensive Security Hardening
We have implemented enterprise-grade security controls addressing all high-priority vulnerabilities identified in the security audit.
*   **SSRF Protection:** URL validation blocks localhost, private IPs, and dangerous schemes to prevent Server-Side Request Forgery attacks.
*   **Input Validation:** Centralized `InputValidator` class with OWASP-compliant validation rules for all user inputs.
*   **Session Expiration:** Automatic session cleanup with activity-based expiration (1 hour default) to prevent memory leaks.
*   **Error Sanitization:** Environment-aware error messages (generic in production, detailed in development) to prevent information disclosure.
*   **Input Length Limits:** Protection against memory exhaustion with configurable limits (name: 100, answer: 5000, JD: 10000 chars).

### 2. Security Test Suite
*   **Comprehensive Coverage:** 25 security tests covering all implemented fixes.
*   **100% Pass Rate:** All security tests passing, 82/83 overall tests passing.
*   **Test Execution:** Fast test suite (6.88s) with comprehensive coverage.

### 3. Documentation & Audit
*   **Security Audit Report:** Complete audit findings documented in `docs/AUDIT_REPORT.md`.
*   **Implementation Guide:** Detailed security implementation documentation in `docs/SECURITY_IMPLEMENTATION.md`.
*   **Troubleshooting:** Added security troubleshooting section for common validation issues.

---

## 🛠️ Technical Changelog

### Added
*   `src/ai_interviewer/utils/input_validator.py`: Centralized input validation module with SSRF protection utilities.
*   `tests/test_security_fixes.py`: Comprehensive security test suite (25 tests).
*   `docs/AUDIT_REPORT.md`: Complete security audit findings and recommendations.
*   `docs/SECURITY_IMPLEMENTATION.md`: Detailed security implementation documentation.

### Changed
*   **Security:** Added SSRF protection to `src/ai_interviewer/utils/url_scraper.py` with URL validation and IP checking.
*   **Security:** Enhanced `src/ai_interviewer/controller.py` with input validation and error sanitization.
*   **Security:** Updated `src/ai_interviewer/core/session_manager.py` with session expiration and automatic cleanup.
*   **Config:** Added security constants to `src/ai_interviewer/utils/config.py` (input limits, session expiration).
*   **Documentation:** Updated README.md, docs/CHANGELOG.md, and troubleshooting guides with security features.

### Fixed
*   **SSRF Vulnerability:** Blocked localhost and private IP access in URL scraper.
*   **Memory Exhaustion:** Added input length limits to prevent DoS attacks.
*   **Information Disclosure:** Sanitized error messages in production mode.
*   **Session Leaks:** Implemented automatic session expiration and cleanup.

---

## 🔒 Security Improvements

### Threat Model Addressed
1. **SSRF (Server-Side Request Forgery)** - HIGH → LOW
   - URL validation blocks localhost, private IPs, dangerous schemes
   - Response size limits prevent resource exhaustion

2. **Input Injection** - MEDIUM → LOW
   - Length limits, character validation, XSS pattern detection
   - Comprehensive validation for all user inputs

3. **Information Disclosure** - MEDIUM → LOW
   - Environment-aware error sanitization
   - Generic messages in production, detailed in development

4. **Memory Exhaustion** - MEDIUM → LOW
   - Input length limits (name: 100, answer: 5000, JD: 10000 chars)
   - Response size limits in URL scraper

5. **Session Hijacking/Leakage** - LOW → VERY LOW
   - Automatic session expiration (1 hour inactivity)
   - Thread-safe session management with cleanup

---

## 📊 Test Results

**Security Test Suite:**
- ✅ 25/25 security tests passed (100%)
- ✅ Execution time: 6.88s
- ✅ Coverage: Input validation, SSRF protection, session expiration, error sanitization

**Full Test Suite:**
- ✅ 82/83 tests passed (98.8%)
- ✅ 1 pre-existing failure (unrelated to security fixes)

---

## 📚 Documentation

*   **Security Audit:** See [docs/AUDIT_REPORT.md](docs/AUDIT_REPORT.md) for complete audit findings.
*   **Implementation Details:** See [docs/SECURITY_IMPLEMENTATION.md](docs/SECURITY_IMPLEMENTATION.md) for technical details.
*   **Troubleshooting:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for security-related issues.

---

# 🚀 AI Interviewer v3.2.0: Modular Architecture

**Release Date:** December 14, 2025  
**Tag:** `v3.2.0`  
**Focus:** Clean Architecture, Modular UI, and Company Intelligence.

---

## 🌟 Major Highlights

### 1. Modular UI Architecture (Clean Architecture)
We have successfully decoupled the Presentation Layer (`src/ui/`) from the Business Logic (`controller.py`).
*   **Decoupled Logic:** The Controller now returns pure data dictionaries, making it testable without a browser.
*   **Adapter Pattern:** `InterviewHandlers` acts as the bridge, converting raw data into Gradio UI updates.
*   **Scalability:** New features can be added to the UI without risking the core intelligence engine.

### 2. Company-Specific Intelligence
The system can now adapt its questioning strategy based on the detected target company.
*   **Amazon:** Focuses on "Leadership Principles" (Customer Obsession, Ownership).
*   **Google:** Focuses on "Googleyness" and General Cognitive Ability (GCA).
*   **Dynamic Injection:** Strategies are injected into the reasoning engine at runtime based on JD parsing.

---

# 🚀 AI Interviewer v3.0.0: The Cognitive Upgrade

**Release Date:** December 12, 2025  
**Tag:** `v3.0.0`  
**Focus:** Micro-Services, Metacognition, and Cloud-Native Deployment.

---

## 🌟 Major Highlights

### 1. From Monolith to Micro-Services
We have completely decomposed the legacy `AutonomousInterviewer` God class into focused, testable micro-services:
*   **🧠 Orchestrator (`autonomous_interviewer.py`):** Acts as the central nervous system, coordinating logic but delegating heavy lifting.
*   **💾 State Layer (`session_manager.py`):** Isolated state management for thread-safe concurrent sessions.
*   **📚 RAG Service (`rag_service.py`):** "Grounded Knowledge" engine that verifies candidate answers against technical documentation.
*   **🕵️ Critic Service (`critic_service.py`):** "Reflexion Agent" that self-critiques questions before asking them to ensure quality and lack of bias.
*   **📈 Learning Service (`learning_service.py`):** "Reasoning Bank" that remembers successful interview patterns.

### 2. Autonomous Cognitive Architecture
The system no longer runs on simple if-else heuristics. It now **thinks**:
*   **Chain-of-Thought (CoT):** Every decision (greeting, question, evaluation) is preceded by a "Thought Process" logged in the system.
*   **Self-Correction:** If the generated question is too hard or biased, the Critic Service rejects it and forces a regeneration.

### 3. Cloud-Native & Docker Ready
*   **Dockerized:** A production-ready `Dockerfile` optimized for Hugging Face Spaces (running as non-root user `1000`).
*   **CI/CD:** Automated GitHub Actions workflow (`sync_to_hub.yml`) to deploy changes instantly to the cloud.
*   **Stateless:** Designed to be stateless (session state is decoupled) allowing for future horizontal scaling.

---

## 🛠️ Technical Changelog

### Added
*   `src/ai_interviewer/core/session_manager.py`: ACID-like transaction management for interview sessions.
*   `src/ai_interviewer/modules/rag_service.py`: Vector DB (ChromaDB) integration for fact-checking.
*   `src/ai_interviewer/modules/critic_service.py`: LLM-based query validator.
*   `.github/workflows/sync_to_hub.yml`: Continuous Deployment pipeline.
*   `Dockerfile`: Multi-stage python build for reduced image size.

### Changed
*   **Refactor:** Moved all core logic from `main.py` to `src/ui/app.py`.
*   **API:** `AutonomousInterviewer` now returns a simplified dict structure, hiding internal complexity.
*   **Tests:** Completely rewrote `test_production.py` to support the decoupled `SessionManager`.

### Fixed
*   **Concurrency:** Resolved race conditions in session handling by introducing `threading.Lock` in `AutonomousFlowController`.
*   **Privacy:** Added PII redaction guardrails in the logging layer.

---

## 🐛 Bug Reporting & Feedback

We have introduced standard Issue Templates to make reporting easier:
1.  **Bug Report:** For reporting crashes or logic errors.
2.  **Feature Request:** For proposing new skills or modules.

*To open a discussion, please use the **Discussions** tab in this repository.*

---

## 📦 How to Deploy

### Option 1: Docker (Recommended)
```bash
docker build -t ai-interviewer:v3 .
docker run -p 7860:7860 -e HF_TOKEN=your_token ai-interviewer:v3
```

### Option 2: Local Python
```bash
pip install -r requirements.txt
python main.py
```

