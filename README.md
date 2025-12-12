---
title: AI Technical Interviewer
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
app_file: main.py
pinned: false
license: mit
---

<div align="center">

# 🤖 Autonomous AI Technical Interviewer

### *Your AI-Powered Interview Coach with Human-Like Intelligence*

[![Live Demo](https://img.shields.io/badge/🚀_Try_Live_Demo-HuggingFace_Spaces-FF6B6B?style=for-the-badge)](https://huggingface.co/spaces/Vikas9793/ai-interviewer)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/VIKAS9793/ai-interviewer-langchain)
[![CI/CD](https://github.com/VIKAS9793/ai-interviewer-langchain/actions/workflows/sync_to_hub.yml/badge.svg)](https://github.com/VIKAS9793/ai-interviewer-langchain/actions)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

![Version](https://img.shields.io/badge/Release-v3.0.1-blue?style=flat-square&logo=git)
![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-4.44.0-FF7C00?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-Powered-blue?style=flat-square)
![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-API-FFD21E?style=flat-square)
![LLaMA](https://img.shields.io/badge/LLaMA_3-8B-0467DF?style=flat-square)

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

---

## 📚 Supported Interview Topics

| Domain | Focus Areas |
|--------|-------------|
| **Python/Backend** | FastAPI/Flask, Asyncio, ORM, Django, REST APIs |
| **JavaScript/Frontend** | React, Vue, Modern JS (ES6+), DOM, Web Performance |
| **System Design & Architecture** | Scalability, Microservices, Load Balancing, Caching |
| **Data Structures & Algorithms** | Trees, Graphs, DP, Sorting, Complexity Analysis |
| **Machine Learning/AI** | Transformers, Deep Learning, NLP, RAG Pipelines |
| **Cloud & DevOps** | AWS/GCP/Azure, Docker/K8s, CI/CD, Terraform |
| **Database & SQL** | SQL, NoSQL, Indexing, Query Optimization |
| **API Design & REST** | RESTful Design, GraphQL, Authentication, Rate Limiting |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User([User]) <--> UI[Gradio UI]
    UI <--> Main["App Controller (Main)"]
    
    subgraph "Core Engine (Orchestrator)"
        AutoInt[AutonomousInterviewer]
    end
    
    subgraph "State Layer"
        SM[SessionManager]
        DB[(Session DB)]
        SM <--> DB
    end
    
    subgraph "Cognitive Services (Modules)"
        RAG[RAG Service]
        Critic[Critic Service]
        Learn[Learning Service]
        
        RAG <--> VDB[(Vector Store)]
        Learn <--> RB[(Reasoning Bank)]
    end
    
    Main --> AutoInt
    AutoInt --> SM
    
    AutoInt -- "Context" --> RAG
    AutoInt -- "Draft" --> Critic
    AutoInt -- "Trajectory" --> Learn
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

## 🆘 Support & Feedback

*   🐛 **Found a bug?** [Open a Bug Report](https://github.com/VIKAS9793/ai-interviewer-langchain/issues/new?template=bug_report.md)
*   💡 **Have an idea?** [Request a Feature](https://github.com/VIKAS9793/ai-interviewer-langchain/issues/new?template=feature_request.md)
*   💬 **Questions?** [Join the Discussion](https://github.com/VIKAS9793/ai-interviewer-langchain/discussions)

---

## 📈 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v3.0.1** | 2025-12-12 | 🔥 Hotfix: Fixed scoring, question counter, feedback, topics |
| **v3.0.0** | 2025-12-12 | [**The Cognitive Upgrade**](RELEASE_NOTES.md): Reasoning, RAG, Reflexion, Micro-Services |
| **v2.6.0** | 2025-12-12 | 🎨 UI Overhaul (Dark Mode, Pill Buttons, High Contrast) |
| **v2.5.1** | 2025-12-11 | Hotfix: Gradio 4.44 downgrade, Torch/Triton conflict |
| **v2.5.0** | 2025-12-11 | Practice Mode (Resume + JD), 11 bug fixes |
| **v2.4.0** | 2025-12-10 | Voice Mode (browser-native STT/TTS) |

---

<div align="center">

### ⭐ Star this repo if you find it useful!

[![GitHub stars](https://img.shields.io/github/stars/VIKAS9793/ai-interviewer-langchain?style=social)](https://github.com/VIKAS9793/ai-interviewer-langchain)
[![GitHub forks](https://img.shields.io/github/forks/VIKAS9793/ai-interviewer-langchain?style=social)](https://github.com/VIKAS9793/ai-interviewer-langchain/fork)

---

**Built with ❤️ using LangChain, HuggingFace, and Gradio**

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

</div>