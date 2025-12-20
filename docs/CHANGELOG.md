# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.5.1] - 2025-12-20

### Added
- **File upload support** for resume parsing via ADK artifacts
- PDF text extraction using PyPDF2
- DOCX text extraction using python-docx
- Artifact handling in `resume_parser` tool
- Graceful fallback if file parsing libraries unavailable

### Changed
- `parse_resume` function now accepts `tool_context` parameter
- Enhanced error handling for uploaded file processing

### Dependencies
- Added `PyPDF2>=3.0.0` for PDF parsing
- Added `python-docx>=1.1.0` for DOCX parsing

### Testing
- Status: Pending (quota blocked)
- Integration tests planned for all file formats

---

## [4.5.0] - 2025-12-20

### Added - Critic Agent Integration 💬

- **critic_agent**: Integrated into root orchestrator
  - Validates question quality and fairness
  - Provides answer critique and improvement suggestions
  - Supports study mode for educational feedback

### Architecture
- Sub-agents: 5 → 6 (added critic_agent)

### Testing
- ✅ Import tests passed
- ⏸️ Browser testing pending quota reset
- 🔒 Local commit (e9038d3)

---

## [4.4.0] - 2025-12-20

### Added - Interview Difficulty Modes 🎚️

**Three interview tracks following NotebookLM Fast/Deep Research pattern**

- **Quick Screen** (15 min)
  - 3-5 easy/medium questions
  - Surface-level evaluation
  - Binary pass/fail
  
- **Standard Interview** (45 min)
  - 8-12 balanced questions
  - Comprehensive assessment
  - Multi-agent scoring
  
- **Deep Technical** (90 min)
  - 15-20 hard/expert questions
  - In-depth evaluation
  - Full multi-dimensional analysis

### Implementation
- `difficulty_modes.py`: Mode configuration with question distribution
- Enhanced interviewer_agent instruction for mode awareness
- Automatic difficulty progression

### Testing
- ✅ Configuration tests passed
- ⏸️ Browser testing pending quota reset
- 🔒 Local commit (18fc742)

---

## [4.3.0] - 2025-12-20

### Added - Multi-Agent Scoring System 🎯

**Parallel evaluation across multiple dimensions**

- **scoring_coordinator**: Orchestrates specialist scorers
  - Delegates to 3 independent evaluators
  - Weighted aggregation (40% technical, 30% communication, 30% problem-solving)
  - JSON-structured comprehensive assessment
  
- **technical_scorer**: Code correctness, quality, efficiency, best practices
- **communication_scorer**: Clarity, structure, completeness, professionalism  
- **problem_solving_scorer**: Approach, analytical thinking, creativity, methodology

### Architecture
- Nested multi-agent pattern (coordinator + 3 sub-scorers)
- Follows Google AI multi-perspective evaluation pattern

### Testing
- ✅ Import tests passed (3 scorers under coordinator)
- ⏸️ Browser testing pending quota reset
- 🔒 Local commit (529301c)

---

## [4.2.0] - 2025-12-20

### Added - Guided Learning Mode 🎓

**Educational interview preparation following Google AI 2025 patterns**

- **study_agent**: Educational tutor using Socratic method
  - Helps candidates LEARN through guided discovery
  - Never gives direct solutions, encourages thinking
  - Follows Gemini Guided Learning pattern

- **explain_concept tool**: CS concept library with examples
  - Data Structures: arrays, BST, hash_maps, graphs
  - Algorithms: binary_search, dynamic_programming  
  - Time/space complexity, use cases, pitfalls, code examples
  - 3 depth levels: quick, standard, deep

- **provide_hints tool**: Progressive 3-level hint system
  - Level 1 (Gentle): Guiding questions, direction
  - Level 2 (Medium): Algorithm/approach suggestions
  - Level 3 (Detailed): Pseudocode, no full solution

### Architecture
- Multi-agent count: 4 → 5 sub-agents
- Aligned with NotebookLM research modes & Gemini Guided Learning

### Testing
- ✅ Local import tests passed
- ⏸️ Browser testing pending quota reset
- 🔒 Local commit (c9d1095)

---

## [4.1.0] - 2025-12-19

### Added
- **Multi-Agent Architecture**: Refactored to ADK sub_agents pattern for code execution compatibility
  - `interviewer_agent`: Question generation and answer evaluation (2 tools)
  - `resume_agent`: Resume parsing and job description analysis (2 tools)
  - `coding_agent`: Python code execution with `BuiltInCodeExecutor` (sandboxed)
  - `root_agent`: Orchestrator coordinating all specialists
- **Code Execution**: Verified working - agent can generate and execute Python code safely
- **Smart Routing**: Automatically routes tasks to appropriate specialist sub-agent

### Changed
- Root agent refactored from tool-based to orchestrator pattern
- Interviewer agent now focused solely on Q&A (resume tools moved to resume_agent)

### Technical
- Resolves ADK limitation: built-in tools cannot coexist with custom tools in same agent
- Uses official ADK sub_agents pattern per documentation
- Maintains single `root_agent` entry point (ADK discovery unchanged)
- Zero breaking changes - external interface identical

### Audit Impact
- **A1 (Single root_agent)**: ✅ Maintained
- **A3 (Workflow dead code)**: ✅ Resolved
- **T1-T3 (Tools)**: ✅ Maintained

---

## [4.0.0] - 2025-12-18

Initial Google ADK migration from LangChain.
