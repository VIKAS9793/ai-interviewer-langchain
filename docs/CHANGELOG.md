# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- ✅ **A1** (Single root_agent): Maintained - orchestrator pattern
- ✅ **A3** (Workflow dead code): **RESOLVED** - Multi-agent IS the workflow
- ✅ **G1** (Safety agents): Prepared for integration
- ✅ **T1-T3**: Maintained - tools now in sub-agents

---

## [4.0.0] - 2025-12-19

### 🚀 Major Release: Google ADK Migration

Complete rewrite using Google Agent Development Kit (ADK) for a 100% Google-native experience.

### Added
- **Google ADK Integration** - Native agent framework
- **ADK Web UI** - Built-in web interface (port 8000)
- **Gemini 2.5 Flash-Lite** - Direct API integration
- **Cloud Run Support** - One-click GCP deployment
- **Session Management** - ADK SessionService with state persistence
- **Safety Guardrails** - Google's native content filtering
- **ToolContext State** - Tools track interview progress across turns
- **Comprehensive Documentation** - Full audit and setup guides

### Changed
- Migrated from LangChain/LangGraph to Google ADK
- Replaced Gradio UI with ADK Web
- Moved from HuggingFace Spaces to Cloud Run
- Simplified codebase (95% reduction - 20,862 deletions)
- Tools now stateful with `ToolContext` integration

### Removed
- LangChain/LangGraph dependencies
- Gradio UI components
- HuggingFace Spaces configuration
- SqliteSaver persistence (replaced by ADK SessionService)
- All stale/unused code (prompts.py, duplicate agents)

###  Fixed
- Canonical `root_agent` entry point (agent.py)
- ADK best practice compliance (no tool defaults)
- All documentation links and paths
- Deploy script Dockerfile reference

### Deprecated
- HuggingFace Spaces deployment (archived)
- Previous v3.x releases

**Audit Status:** ✅ All findings remediated (Phase 0 + Phase 1)  
**Testing:** 7/7 automated tests pass, end-to-end validated

---

## [3.3.2] - 2025-12-18 (HuggingFace - Deprecated)

### Fixed
- UI text redaction (white boxes) in Gradio
- Bracket escaping for markdown rendering

---

## [3.3.1] - 2025-12-17 (HuggingFace - Deprecated)

### Fixed
- Session persistence issues
- Token exhaustion handling
- Fallback question repetition

---

## [3.3.0] - 2025-12-16 (HuggingFace - Deprecated)

### Added
- LangGraph state machine architecture
- SqliteSaver for persistence
- Semantic deduplication
- TTD (Time-Travel Diffusion) generator

---

## Migration Guide

See [ADR-001: Migration to Google ADK](docs/ADR/001-migration-to-google-adk.md) for details on:
- Why we migrated
- What changed
- How to update your setup
