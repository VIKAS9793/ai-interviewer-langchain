---
title: AI Technical Interviewer
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.0.2
python_version: "3.11"
app_file: main.py
pinned: false
license: mit
---

<div align="center">

# 🤖 Autonomous AI Technical Interviewer

### *Your AI-Powered Interview Coach with Human-Like Intelligence*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-HuggingFace_Spaces-FF6B6B?style=for-the-badge)](https://huggingface.co/spaces/Vikas9793/ai-interviewer)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

[![LangChain](https://img.shields.io/badge/LangChain-Powered-1C3C3C?style=flat-square&logo=chainlink)](https://langchain.com)
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-Inference_API-FFD21E?style=flat-square)](https://huggingface.co)
[![Gradio](https://img.shields.io/badge/Gradio-UI-FF7C00?style=flat-square&logo=gradio)](https://gradio.app)

---

**Self-thinking AI** • **Chain-of-Thought Reasoning** • **Hybrid Evaluation** • **Responsible AI**

[Try Live Demo](https://huggingface.co/spaces/Vikas9793/ai-interviewer) · [Documentation](docs/) · [Report Bug](https://github.com/VIKAS9793/ai-interviewer-langchain/issues)

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
        A[👤 Candidate Input] --> B[Interview Controller]
    end
    
    subgraph Core["⚙️ Core Engine"]
        B --> C[🤖 Autonomous Interviewer]
        C --> D[🧠 Reasoning Engine]
        C --> E[📊 Evaluation Engine]
    end
    
    subgraph LLMs["🤗 HuggingFace Models"]
        D --> F["LLaMA-3-8B\n📝 Questions"]
        E --> G["Qwen2.5-32B\n⭐ Evaluation"]
        E --> H["MiniLM\n🔍 Embeddings"]
    end
    
    subgraph Safety["🛡️ AI Safety"]
        C --> I[Guardrails]
        I --> J[Bias Check]
        I --> K[Fairness]
    end
    
    style UI fill:#e1f5fe
    style Core fill:#fff3e0
    style LLMs fill:#f3e5f5
    style Safety fill:#e8f5e9
```

---

## 📊 Evaluation System

```mermaid
pie title Scoring Weights
    "LLM Score (Qwen2.5)" : 60
    "Heuristic Score" : 40
```

| Score | Level | Description |
|:-----:|:------|:------------|
| ⭐⭐⭐⭐⭐ | **Exceptional** | Comprehensive, accurate, well-structured with examples |
| ⭐⭐⭐⭐ | **Good** | Covers main concepts correctly, minor gaps |
| ⭐⭐⭐ | **Adequate** | Addresses question but lacks depth |
| ⭐⭐ | **Limited** | Partially relevant, significant gaps |
| ⭐ | **Poor** | Off-topic or incorrect |

---

## � Quick Start

### Live Demo (Recommended)
```
🌐 https://huggingface.co/spaces/Vikas9793/ai-interviewer
```

### Local Installation
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

## � Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | LangChain + Gradio |
| **Question Gen** | Meta-Llama-3-8B-Instruct |
| **Evaluation** | Qwen2.5-32B-Instruct |
| **Embeddings** | Sentence Transformers |
| **Deployment** | HuggingFace Spaces |

---

## 📚 Interview Topics

- 💻 JavaScript/Frontend Development
- 🐍 Python/Backend Development
- 🤖 Machine Learning/AI
- 🏗️ System Design
- 📈 Data Structures & Algorithms

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP.md) | Installation instructions |
| [Architecture](docs/ARCHITECTURE.md) | System design & diagrams |
| [ADR](docs/ADR.md) | Architectural decisions |
| [Roadmap](docs/ROADMAP.md) | Future plans |
| [Changelog](CHANGELOG.md) | Version history |

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

<div align="center">

### ⭐ Star this repo if you find it useful!

**Built with ❤️ using LangChain, HuggingFace, and Gradio**

[![GitHub stars](https://img.shields.io/github/stars/VIKAS9793/ai-interviewer-langchain?style=social)](https://github.com/VIKAS9793/ai-interviewer-langchain)

</div>