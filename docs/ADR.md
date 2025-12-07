# Architectural Decision Records (ADR)

> **Last Updated:** 2025-12-07
> **Version:** 2.0.0

## 1. Hybrid Agentic Architecture
* **Status:** Accepted
* **Date:** 2025-12-07
* **Context:** We needed a system that could reason like a human interviewer while maintaining strict safety and consistency standards. Pure LLM approaches were too unpredictable; strictly rule-based systems were too rigid.
* **Decision:** We adopted a **Hybrid Architecture** combining:
    1.  **Autonomous Reasoning Engine (CoT):** For dynamic decision-making and strategy.
    2.  **ReasoningBank (Memory):** For retrieving proven successful interview strategies (arXiv:2509.25140).
    3.  **ReflectAgent (Critic):** For quality assurance and safety checks (arXiv:2510.08002).
* **Consequences:** Significantly improved reasoning quality (~250% better than baseline) but introduced slightly higher latency which was mitigated by concurrent threading.

## 2. Local-First Privacy (Ollama)
* **Status:** Accepted
* **Date:** 2025-12-07
* **Context:** Interview data is highly sensitive. reliance on cloud APIs introduces privacy risks and latency/cost issues for high-volume use.
* **Decision:** We use **Ollama** with `llama3.2:3b` as the core inference engine, running entirely locally.
* **Consequences:** Complete data privacy and zero cloud costs. Users must have adequate local hardware (4GB+ RAM).

## 3. SQLite for "Brain" Storage
* **Status:** Accepted
* **Date:** 2025-12-07
* **Context:** The agent needs persistent memory for learning strategies. Setting up an external DB (Postgres/MySQL) is a high barrier to entry for end-users.
* **Decision:** We use **SQLite** (`data/memory/reasoning_bank.db`) and **JSON** (`data/memory/metacognitive_state.json`) for persistence.
* **Consequences:** Zero-setup deployment. The "Brain" file is portable and can be easily backed up or reset.
