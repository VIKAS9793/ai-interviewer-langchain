# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.7.0] - 2025-12-24 (Experimental)

### Added - A2UI Web Interface 🌐
- **A2A-ADK Protocol Bridge** - FastAPI server translating A2A JSON-RPC to ADK REST
- **A2UI Lit Renderer** - Google's component-based UI framework
- **Interview Surface** - Text components rendering in beautiful gradient UI
- **Custom Interviewer Config** - `a2ui-repo/samples/client/lit/shell/configs/interviewer.ts`

### Architecture
```
A2UI Frontend (Lit) → A2A Bridge (:10002) → ADK Backend (:8000)
```

### New Files
- `src/adk_interviewer/a2ui/bridge.py` - Protocol bridge server
- `src/adk_interviewer/a2ui/components.py` - A2UI component schemas
- `docs/A2UI_INTEGRATION_JOURNEY.md` - Complete integration journey

### Challenges Overcome
- Protocol mismatch (A2A JSON-RPC ↔ ADK REST)
- SSE response parsing
- A2UI component format (`component` key, `literalString` wrapper)
- JSON-RPC 2.0 compliance (`id` field matching)

### To Run
```bash
# 3 terminals required
adk web ./src                           # ADK Backend
python -m src.adk_interviewer.a2ui.bridge  # A2A Bridge
cd a2ui-repo/samples/client/lit/shell && npm run dev  # Frontend
```

---

## [4.6.0] - 2025-12-22

### Added - Sequential Safety Pattern 🛡️
- **Risk Assessment** in `coding_agent` - Blocks dangerous code before execution
- **10 Risk Patterns** detected: eval, exec, system commands, file operations, network requests
- **Context Files** - Conductor-style project configuration (`.adk/`)
  - `product.md` - Interview goals and target roles
  - `tech_stack.md` - Question topics and tech preferences
  - `workflow.md` - Evaluation rubrics and feedback standards

### Changed
- **coding_agent** now includes automatic safety screening
- Architecture follows Kaggle AI Agent competition winning patterns

### Inspiration
Based on Kaggle 5-Day AI Agent Intensive (11,000 teams):
- Sequential Safety (confirmation gates)
- Context-driven development (Conductor pattern)
- Quality over prompts (architecture wins)

### Testing
- Import test: ✅ Passed (6 agents)
- Risk assessment function: Ready for integration testing

---

## [4.5.2] - 2025-12-21

### Fixed
- **Study Mode Literal Type Error** - Changed `hint_level: Literal[1,2,3]` to `int` and `depth: Literal[...]` to `str` for ADK compatibility
- **Unused Import** - Removed unused `from typing import Literal` in concept_explainer.py

### Changed
- **Study Mode Expanded** - Now covers ALL interview topics (PM, Business, Design, etc.), not just CS/algorithms
- **Dynamic Concept Explanations** - explain_concept tool now uses Gemini's knowledge for non-CS topics
- **README Updated** - File upload feature clarified due to Gemini API MIME type limitations

### Tested ✅
- Safety Agent - Correctly declined harmful requests
- Interview Evaluation - Provided quality feedback
- Code Understanding - Recognized Dijkstra's algorithm
- Study Mode Transfer - Works after Literal type fix

### Known Limitations
- File upload (PDF/DOCX) limited by Gemini API MIME type support
- Recommend paste-text for resume analysis

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
- Status: Partial (quota limited)
- Core features validated

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
- **Multi-Agent Architecture**: Refactored to ADK sub_agents pattern
  - `interviewer_agent`: Question generation and answer evaluation (2 tools)
  - `resume_agent`: Resume parsing and job description analysis (2 tools)
  - `coding_agent`: Python code analysis and review
  - `root_agent`: Orchestrator coordinating all specialists
- **Code Analysis**: Agent can review and analyze Python code
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
