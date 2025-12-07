# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-12-07

### 🚀 Major Release: The "Hybrid Architecture" Update

This release marks a fundamental shift from a simple LLM wrapper to a true **Autonomous Agent**. We have implemented a hybrid architecture inspired by cutting-edge research in agentic AI.

### ✨ New Features
*   **ReasoningBank (Memory System):** Implemented a persistent memory system that allows the agent to learn strategies from past interviews.
    *   *Citation:* "ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory" (arXiv:2509.25140)
*   **ReflectAgent (Critic):** Added a self-reflection loop that evaluates question fairness and scoring consistency before finalizing decisions.
    *   *Citation:* "MUSE: The Reflect Agent" (arXiv:2510.08002)
*   **Metacognitive System:** Enabled self-assessment capabilities where the agent tracks its own proficiency in different topics.
    *   *Citation:* "Intrinsic Metacognitive Learning" (arXiv:2506.05109)
*   **Shadow Mode Integration:** New modules operate in a robust "Shadow Mode" to provide value without risking system stability.

### 🛠️ Improvements
*   **Architecture Overhaul:** Refactored entire codebase into a clean `src/` modular structure. Removed all legacy spaghetti code.
*   **Centralized Data:** All persistent data now lives in `data/memory/` for easier management.
*   **Dependency Locking:** `requirements.txt` is now strictly pinned for production stability.
*   **Documentation:** Complete documentation rewrite including ADRs, Setup Guide, and Architecture diagrams.

### 🗑️ Removals
*   Removed `enhanced_main.py` (consolidated into `main.py`).
*   Removed `legacy/` directory.
*   Deleted unused utility scripts (`connection_pool.py`, `health_check.py`) to reduce bloat.
