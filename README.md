---
title: AI Technical Interviewer
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
python_version: "3.11"
app_file: main.py
pinned: false
license: mit
---

<div align="center">

# 🤖 Autonomous AI Technical Interviewer

### *Your AI-Powered Interview Coach with Human-Like Intelligence*

[![Live Demo](https://img.shields.io/badge/🚀_Try_Live_Demo-HuggingFace_Spaces-FF6B6B?style=for-the-badge)](https://huggingface.co/spaces/Vikas9793/ai-interviewer)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/VIKAS9793/ai-interviewer-langchain)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-5.9.1-FF7C00?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=flat-square)
![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-API-FFD21E?style=flat-square)
![LLaMA](https://img.shields.io/badge/LLaMA_3-8B-0467DF?style=flat-square)
![Qwen](https://img.shields.io/badge/Qwen_2.5-32B-7C3AED?style=flat-square)

**Self-Thinking AI** • **Chain-of-Thought** • **Hybrid Evaluation** • **Responsible AI**

</div>

---

## ✨ Features at a Glance

<table>
<tr>
<td width="50%">

### 🧠 Intelligent Reasoning
- Chain-of-Thought before every action
- Self-reflection and improvement
- Adaptive difficulty adjustment

</td>
<td width="50%">

### 📊 Hybrid Evaluation
- Dual-model scoring (LLaMA + Qwen2.5)
- Prometheus-style 1-5 rubric
- Semantic relevance checking

</td>
</tr>
<tr>
<td width="50%">

### 🛡️ Responsible AI
- Bias detection & mitigation
- Fairness validation
- Transparent decision-making

</td>
<td width="50%">

### ⚡ Cloud-Native
- HuggingFace Spaces ready
- No GPU required
- Instant deployment

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph UI["🖥️ Gradio Interface"]
        A["👤 Candidate"] --> B["Interview Controller"]
    end
    
    subgraph Core["⚙️ Core Engine"]
        B --> C["🤖 Autonomous Interviewer"]
        C --> D["🧠 Reasoning Engine<br/>Chain-of-Thought"]
        C --> E["📊 Evaluation Engine<br/>Hybrid Scoring"]
        C --> F["📚 Knowledge Grounding"]
    end
    
    subgraph Models["🤗 HuggingFace Cloud"]
        D --> G["Meta LLaMA-3-8B<br/>Question Generation"]
        E --> H["Qwen2.5-32B<br/>Answer Evaluation"]
        E --> I["MiniLM<br/>Semantic Embeddings"]
    end
    
    subgraph Safety["🛡️ AI Guardrails"]
        C --> J["Bias Detection"]
        C --> K["Fairness Validation"]
        C --> L["Explainability"]
    end
    
    style UI fill:#e3f2fd,stroke:#1976d2
    style Core fill:#fff3e0,stroke:#f57c00
    style Models fill:#f3e5f5,stroke:#7b1fa2
    style Safety fill:#e8f5e9,stroke:#388e3c
```

---

## 📊 Evaluation System

```mermaid
pie title Scoring Distribution
    "LLM Score (Qwen2.5)" : 60
    "Heuristic Score" : 40
```

| Score | Level | Criteria |
|:-----:|:------|:---------|
| ⭐⭐⭐⭐⭐ | **Exceptional** | Comprehensive, accurate, well-structured with examples |
| ⭐⭐⭐⭐ | **Good** | Covers main concepts correctly |
| ⭐⭐⭐ | **Adequate** | Addresses question but lacks depth |
| ⭐⭐ | **Limited** | Partially relevant, gaps/errors |
| ⭐ | **Poor** | Off-topic or incorrect |

---

## 🚀 Quick Start

### ☁️ Live Demo (Recommended)

<div align="center">

[![Try Now](https://img.shields.io/badge/🌐_Try_Now-huggingface.co/spaces/Vikas9793/ai--interviewer-FF6B6B?style=for-the-badge)](https://huggingface.co/spaces/Vikas9793/ai-interviewer)

</div>

### 💻 Local Installation
```bash
# Clone & Setup
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain
pip install -r requirements.txt

# Configure & Run
export HF_TOKEN="your_token"
python main.py
```

---

## 📚 Interview Topics

| Topic | Icon |
|-------|------|
| JavaScript/Frontend | � |
| Python/Backend | 🐍 |
| Machine Learning/AI | 🤖 |
| System Design | 🏗️ |
| Data Structures & Algorithms | 📈 |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| 📋 [Setup Guide](docs/SETUP.md) | Installation & configuration |
| 🏗️ [Architecture](docs/ARCHITECTURE.md) | System design & diagrams |
| 📝 [ADR](docs/ADR.md) | Architectural decisions |
| 🗺️ [Roadmap](docs/ROADMAP.md) | Future plans |
| 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues |
| 📜 [Changelog](CHANGELOG.md) | Version history |
| 🤝 [Contributing](CONTRIBUTING.md) | Contribution guide |

---

## 📈 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v2.2.2** | 2025-12-08 | Codebase cleanup, cloud-first |
| **v2.2.1** | 2025-12-08 | Hybrid evaluation, Prometheus rubrics |
| **v2.2.0** | 2025-12-08 | AI Internal Monologue, Semantic checking |
| **v2.1.0** | 2025-12-07 | HuggingFace Spaces deployment |
| **v2.0.0** | 2025-12-07 | Autonomous Agent architecture |

---

<div align="center">

### ⭐ Star this repo if you find it useful!

[![GitHub stars](https://img.shields.io/github/stars/VIKAS9793/ai-interviewer-langchain?style=social)](https://github.com/VIKAS9793/ai-interviewer-langchain)
[![GitHub forks](https://img.shields.io/github/forks/VIKAS9793/ai-interviewer-langchain?style=social)](https://github.com/VIKAS9793/ai-interviewer-langchain/fork)

---

**Built with ❤️ using LangChain, HuggingFace, and Gradio**

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>