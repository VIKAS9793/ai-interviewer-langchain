# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.0.0] - 2025-12-18

### 🚀 Major Release: Google ADK Migration

Complete rewrite using Google Agent Development Kit (ADK) for a 100% Google-native experience.

### Added
- **Google ADK Integration** - Native agent framework
- **ADK Web UI** - Built-in web interface
- **Gemini 2.5 Flash-Lite** - Direct API integration
- **Cloud Run Support** - One-click GCP deployment
- **Session Management** - ADK SessionService
- **Safety Guardrails** - Google's native filtering

### Changed
- Migrated from LangChain/LangGraph to Google ADK
- Replaced Gradio UI with ADK Web
- Moved from HuggingFace Spaces to Cloud Run
- Simplified codebase (50% reduction)

### Removed
- LangChain/LangGraph dependencies
- Gradio UI components
- HuggingFace Spaces configuration
- SqliteSaver persistence

### Deprecated
- HuggingFace Spaces deployment (archived)
- Previous v3.x releases

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
