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

# 🤖 Autonomous AI Technical Interviewer

A self-thinking AI interview system with Chain-of-Thought reasoning, hybrid evaluation, and responsible AI guardrails.

## ✨ Features

- **🧠 Chain-of-Thought:** Self-reasoning before every question
- **📊 Hybrid Evaluation:** Dual-model scoring (LLaMA + Qwen2.5)
- **🎯 Semantic Relevance:** Embedding-based answer checking
- **🔍 AI Internal Monologue:** Transparent decision-making display
- **🛡️ AI Guardrails:** Fair, unbiased, explainable decisions

## 🚀 Usage

1. Enter your name
2. Select an interview topic
3. Click "Start Enhanced Interview"
4. Answer 5 adaptive questions
5. Receive comprehensive feedback with detailed scoring

## ⚙️ Configuration

This Space requires a **Hugging Face API Token** (`HF_TOKEN`) to access models.

Add your token in the Space **Settings** → **Repository Secrets** → `HF_TOKEN`

## 🔧 Models Used

| Purpose | Model |
|---------|-------|
| Questions | Meta-Llama-3-8B-Instruct |
| Evaluation | Qwen2.5-32B-Instruct |
| Embeddings | all-MiniLM-L6-v2 |

## 📚 Topics Available

- JavaScript/Frontend Development
- Python/Backend Development
- Machine Learning/AI
- System Design
- Data Structures & Algorithms

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.