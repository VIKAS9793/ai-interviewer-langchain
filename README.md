---
title: AI Technical Interviewer
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
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
![Gradio](https://img.shields.io/badge/Gradio-4.44.0-FF7C00?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=flat-square)
![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-API-FFD21E?style=flat-square)
![LLaMA](https://img.shields.io/badge/LLaMA_3-8B-0467DF?style=flat-square)
![Architecture](https://img.shields.io/badge/Single_Model-Architecture-10B981?style=flat-square)

**Self-Thinking AI** • **Chain-of-Thought** • **Autonomous Reasoning** • **Responsible AI**

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

### 📊 Autonomous Evaluation
- Single-Model Architecture (LLaMA 3)
- Prometheus-style 1-5 rubric
- Semantic relevance checking

</td>
</tr>
</tr>
<tr>
<td width="50%">

### 🛡️ Responsible AI
- Bias detection & mitigation
- Fairness validation
- Transparent decision-making

</td>
<td width="50%">

### 🎤 Voice Mode (v2.4)
- Browser-native Speech-to-Text
- AI response read aloud
- Zero external API calls

</td>
</tr>
<tr>
<td width="50%">

### 📄 Practice Mode (v2.5)
- Resume upload (PDF/DOCX)
- JD URL scraping
- Role & experience detection

</td>
<td width="50%">

### 🔒 Security
- File magic byte validation
- Macro/script detection
- XSS prevention

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph UI["🖥️ Gradio Interface"]
        A["👤 Candidate"] --> B["Interview Controller"]
        A2["🎤 Voice Input"] --> B
    end
    
    subgraph Core["⚙️ Core Engine"]
        B --> C["🤖 Autonomous Interviewer"]
        C --> D["🧠 Reasoning Engine<br/>Chain-of-Thought"]
        C --> E["📊 Evaluation Engine<br/>Prometheus Scoring"]
        C --> F["📚 Knowledge Grounding"]
    end
    
    subgraph Models["🤗 HuggingFace Cloud"]
        D --> G["Meta LLaMA-3-8B<br/>Single-Model Architecture"]
        E --> G
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
    "LLM Score (LLaMA 3)" : 60
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
| **v2.5.1** | 2025-12-11 | 🔥 Hotfix: Gradio 4.44 downgrade, Torch/Triton conflict resolution |
| **v2.5.0** | 2025-12-11 | Practice Mode (Resume + JD), 11 bug fixes |
| **v2.4.0** | 2025-12-10 | Voice Mode (browser-native STT/TTS) |
| **v2.3.1** | 2025-12-10 | Single-model stability patch |
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