# 🤖 Autonomous AI Interviewer System

## Overview

An **Autonomous AI Technical Interviewer** with human-like capabilities, deployed on HuggingFace Spaces.

| Feature | Description |
|---------|-------------|
| **Self-Thinking** | Chain-of-Thought reasoning before every action |
| **Hybrid Evaluation** | Qwen2.5 + Heuristics with Prometheus-style rubrics |
| **Semantic Relevance** | Embedding-based answer relevance checking |
| **Knowledge Grounding** | Answer verification against authoritative sources |
| **AI Guardrails** | Fair, unbiased, explainable decisions |

## Quick Start

**Live Demo:** https://huggingface.co/spaces/Vikas9793/ai-interviewer

**Local Setup:**
```bash
# Clone and setup
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain
pip install -r requirements.txt

# Set API token
export HF_TOKEN="your_token"

# Run
python main.py
```

## Architecture

```
src/ai_interviewer/
├── core/
│   ├── autonomous_interviewer.py        # Main AI interviewer agent
│   ├── autonomous_reasoning_engine.py   # Chain-of-Thought reasoning
│   ├── autonomous_flow_controller.py    # Session management
│   ├── ai_guardrails.py                 # Responsible AI safety
│   ├── context_engineer.py              # Knowledge grounding
│   ├── reflect_agent.py                 # Self-reflection agent
│   └── metacognitive.py                 # Self-improvement system
├── utils/
│   └── config.py                        # Configuration
└── assets/
    └── banner.jpg                       # UI Banner
```

## Models Used

| Purpose | Model | Provider |
|---------|-------|----------|
| Questions | Meta-Llama-3-8B-Instruct | HuggingFace |
| Evaluation | Qwen2.5-32B-Instruct | HuggingFace |
| Embeddings | all-MiniLM-L6-v2 | Sentence Transformers |

## Key Features

### 1. Hybrid Evaluation Strategy
- **LLM Scoring (60%):** Prometheus-style 1-5 rubric with Qwen2.5
- **Heuristic Scoring (40%):** Length, structure, keywords, depth

### 2. Semantic Relevance Checking
- Embedding-based similarity (Sentence Transformers)
- Detects off-topic answers (threshold: 0.25)

### 3. AI Internal Monologue
- Transparent reasoning chain display
- Shows confidence, approach, and thought process

## Performance

| Metric | Value |
|--------|-------|
| Response Time | 2-5 seconds |
| Eval Accuracy | ~85% human correlation |
| Cache Hit Rate | > 80% |
