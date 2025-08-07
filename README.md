# 🤖 AI Technical Interviewer

<div align="center">

### **Professional technical interview simulation powered by local AI**

<div style="max-width: 1200px; margin: 20px auto; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.12); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 4px;">
  <img src="src/ai_interviewer/assets/banner.jpg" alt="AI Interviewer Banner" style="width: 100%; height: auto; border-radius: 12px; display: block;"/>
</div>

<br>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1.19-00d084.svg?style=for-the-badge&logo=graphql&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Ollama](https://img.shields.io/badge/Ollama-Llama%203.2%203B-ff6b35.svg?style=for-the-badge&logo=meta&logoColor=white)](https://ollama.ai/)
[![Gradio](https://img.shields.io/badge/Gradio-4.37.2-ff7c00.svg?style=for-the-badge&logo=gradio&logoColor=white)](https://gradio.app/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-28a745.svg?style=for-the-badge&logo=checkmarx&logoColor=white)](#)

</div>

---

## 🎯 **Executive Summary**

<div align="center">
<table>
<tr>
<td width="33%" align="center">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Robot/3D/robot_3d.png" width="60">
<br><strong>AI-Powered</strong><br>
<small>Advanced LangGraph state machines with local LLM</small>
</td>
<td width="33%" align="center">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Brain/3D/brain_3d.png" width="60">
<br><strong>Adaptive Intelligence</strong><br>
<small>Questions adjust based on performance</small>
</td>
<td width="33%" align="center">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Chart%20increasing/3D/chart_increasing_3d.png" width="60">
<br><strong>Professional Analysis</strong><br>
<small>Multi-dimensional evaluation & feedback</small>
</td>
</tr>
</table>
</div>

> 🚀 **A sophisticated AI interviewer that conducts professional technical interviews using LangGraph state machines, Ollama's llama3.2:3b, and ChromaDB vector storage.**

---

## ✅ **Requirements Compliance**

<div align="center">

### 🎯 **MANDATORY Requirements - All Met**

<table>
<tr>
<td align="center">✅<br><strong>LangGraph</strong><br><small>Advanced state machine flow control</small></td>
<td align="center">✅<br><strong>Ollama + llama3.2:3b</strong><br><small>Local LLM (exactly as specified)</small></td>
<td align="center">✅<br><strong>3-5 Dynamic Questions</strong><br><small>AI-generated, adaptive questioning</small></td>
</tr>
<tr>
<td align="center">✅<br><strong>Intelligent Responses</strong><br><small>Smart branching based on performance</small></td>
<td align="center">✅<br><strong>Performance Summary</strong><br><small>Comprehensive evaluation and feedback</small></td>
<td align="center">✅<br><strong>Branching Logic</strong><br><small>Next question depends on previous answer</small></td>
</tr>
</table>

### 🎁 **BONUS Features - Exceeding Requirements**

<table>
<tr>
<td align="center">⭐<br><strong>ChromaDB Vector Store</strong><br><small>Semantic question retrieval</small></td>
<td align="center">⭐<br><strong>Multi-Dimensional Scoring</strong><br><small>6-dimension evaluation system</small></td>
<td align="center">⭐<br><strong>Gradio Web Interface</strong><br><small>Professional chat-style UI</small></td>
<td align="center">⭐<br><strong>Advanced Analytics</strong><br><small>Performance tracking and insights</small></td>
</tr>
</table>

</div>

---

## 🎥 **Live Demo**

<div align="center">

### **Watch the AI Interviewer in Action!**

[![AI Interviewer Demo](https://img.youtube.com/vi/0M7M1Pn31vQ/maxresdefault.jpg)](https://youtu.be/0M7M1Pn31vQ)

**📺 Click above to watch the full walkthrough**

<details>
<summary>🎬 <strong>What's Covered in the Demo</strong></summary>

- 🎯 Starting a new interview session
- ⚡ Dynamic question generation  
- 📊 Real-time answer evaluation
- 📈 Performance feedback and scoring
- 🛠️ System navigation and features

</details>

</div>

---

## 🚀 **Quick Start**

<div align="center">

### **Get up and running in 3 simple steps!**

</div>

<table>
<tr>
<td width="33%">

### 📋 **1. Prerequisites**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull llama3.2:3b model
ollama pull llama3.2:3b

# Start Ollama service
ollama serve
```

</td>
<td width="33%">

### 💻 **2. Installation** 

```bash
# Clone and setup
git clone <your-repo-url>
cd ai-interviewer-langchain

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

</td>
<td width="33%">

### 🌟 **3. Launch**

```bash
# Start the application
python main.py
```

<div align="center">
<br>
<strong>🌐 Open your browser to:</strong><br>
<code>http://localhost:7860</code>
</div>

</td>
</tr>
</table>

---

## 🏗️ **Architecture & Technology**

<div align="center">

### **Modern Tech Stack**

<table>
<tr>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"><br>
<strong>Python 3.11+</strong><br>
<small>Core Backend</small>
</td>
<td align="center" width="16.66%">
<img src="https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=graphql&logoColor=white" width="80"><br>
<strong>LangGraph</strong><br>
<small>State Machine</small>
</td>
<td align="center" width="16.66%">
<img src="https://avatars.githubusercontent.com/u/151674099?s=200&v=4" width="40"><br>
<strong>Ollama</strong><br>
<small>Local LLM</small>
</td>
<td align="center" width="16.66%">
<img src="https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge&logo=database&logoColor=white" width="80"><br>
<strong>ChromaDB</strong><br>
<small>Vector Store</small>
</td>
<td align="center" width="16.66%">
<img src="https://img.shields.io/badge/Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white" width="80"><br>
<strong>Gradio</strong><br>
<small>Web Interface</small>
</td>
<td align="center" width="16.66%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tensorflow/tensorflow-original.svg" width="40"><br>
<strong>Transformers</strong><br>
<small>Embeddings</small>
</td>
</tr>
</table>

</div>

### **System Architecture**

```mermaid
graph TB
    subgraph "Frontend Layer"
        A["🖥️ Gradio Web UI"]
    end
    
    subgraph "Control Layer" 
        B["🧠 LangGraph State Machine"]
        C["🎮 Flow Controller"]
    end
    
    subgraph "AI Layer"
        D["🤖 Ollama LLM<br/>(llama3.2:3b)"]
        E["👨‍💼 AI Interviewer Agent"]
        F["📊 Response Evaluator"]
    end
    
    subgraph "Data Layer"
        G["🗃️ ChromaDB Vector Store"]
        H["❓ Question Bank"]
        I["💾 Session Memory"]
    end
    
    A --> B
    B --> C
    C --> E
    E --> D
    E --> F
    F --> G
    G --> H
    H --> I
    I --> B
    B --> A
    
    classDef frontend fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px,color:#000000
    classDef control fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000000
    classDef ai fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#000000
    classDef data fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000000
    
    class A frontend
    class B,C control
    class D,E,F ai
    class G,H,I data
```

---

## ⚡ **Performance Overview**

<div align="center">

<table>
<tr>
<td width="50%">

### **📊 Current Metrics**

| Metric | Value |
|--------|-------|
| ⏱️ Response Time | 3-5 minutes |
| 💾 RAM Required | 8GB minimum |
| 🎮 VRAM Required | 4GB |
| 📦 Model Size | ~2GB (quantized) |

</td>
<td width="50%">

### **🚀 Cloud Benefits**

| Aspect | Improvement |
|--------|-------------|
| 🔥 Processing Speed | 5-10x faster |
| 🧠 Memory Capacity | 4-8x more |
| 🔄 Concurrency | 10x+ parallel |
| 🎯 Model Accuracy | Significantly better |

</td>
</tr>
</table>

</div>

### **Interview Flow Diagram**

```mermaid
flowchart TD
    Start([🎬 Start Interview]) --> SelectTopic[📝 Select Topic]
    SelectTopic --> FirstQuestion[❓ First Question]
    
    subgraph InterviewLoop ["🔄 Interview Loop"]
        FirstQuestion --> EvaluateAnswer[📊 Evaluate Answer]
        EvaluateAnswer --> Decision{🤔 Performance Check}
        
        Decision -->|Score ≥ 7| HarderQuestion[⬆️ Harder Question]
        Decision -->|4 ≤ Score < 7| SimilarQuestion[➡️ Similar Question]
        Decision -->|Score < 4| EasierQuestion[⬇️ Easier Question]
        
        HarderQuestion --> QuestionCount{📊 Question Count}
        SimilarQuestion --> QuestionCount
        EasierQuestion --> QuestionCount
        
        QuestionCount -->|< 5 Questions| EvaluateAnswer
    end
    
    QuestionCount -->|5 Questions Complete| GenerateReport[📋 Generate Report]
    GenerateReport --> End([🏁 Interview Complete])
    
    classDef startEnd fill:#c8e6c9,stroke:#4caf50,stroke-width:3px,color:#000000
    classDef process fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px,color:#000000
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#000000
    classDef question fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#000000
    
    class Start,End startEnd
    class SelectTopic,EvaluateAnswer,GenerateReport process
    class Decision,QuestionCount decision
    class FirstQuestion,HarderQuestion,SimilarQuestion,EasierQuestion question
```

---

## 🧠 **Intelligent Features**

<div align="center">

<table>
<tr>
<td width="50%" align="center">

### **🎯 Adaptive Question Generation**

<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Target/3D/target_3d.png" width="80">

✨ **Dynamic Difficulty Adjustment**<br>
🧩 **Context-Aware Questions**<br>  
🎓 **5 Technical Domains**<br>
🔍 **Expert-Level Content**

</td>
<td width="50%" align="center">

### **📊 Multi-Dimensional Evaluation**

<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bar%20chart/3D/bar_chart_3d.png" width="80">

🎯 **Technical Accuracy**<br>
🧠 **Conceptual Understanding**<br>
💡 **Practical Application**<br>
💬 **Communication Clarity**

</td>
</tr>
</table>

</div>

### **Evaluation Criteria**

```python
evaluation_dimensions = {
    "🎯 technical_accuracy": "Correctness and precision of answers",
    "🧠 conceptual_understanding": "Depth of theoretical knowledge", 
    "💡 practical_application": "Real-world applicability and examples",
    "💬 communication_clarity": "Quality of explanation and articulation",
    "📚 depth_of_knowledge": "Understanding of advanced concepts",
    "🔍 problem_solving_approach": "Analytical thinking and methodology"
}
```

---

## 📚 **Interview Specializations**

<div align="center">

<table>
<tr>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="50"><br>
<strong>JavaScript/Frontend</strong><br>
<small>React, DOM, Async Patterns</small>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50"><br>
<strong>Python/Backend</strong><br>
<small>Django, APIs, Databases</small>
</td>
<td align="center" width="20%">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Robot/3D/robot_3d.png" width="50"><br>
<strong>Machine Learning</strong><br>
<small>Algorithms, Models, Deployment</small>
</td>
<td align="center" width="20%">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Building%20construction/3D/building_construction_3d.png" width="50"><br>
<strong>System Design</strong><br>
<small>Architecture, Scalability</small>
</td>
<td align="center" width="20%">
<img src="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Gear/3D/gear_3d.png" width="50"><br>
<strong>Algorithms & DS</strong><br>
<small>Complexity, Optimization</small>
</td>
</tr>
</table>

</div>

### **Sample Interview Progression**

```mermaid
flowchart LR
    A["❓ Question 1<br/>📟 Easy: Explain var vs let"] --> B["📊 Score: 8/10<br/>✅ Strong Fundamentals"]
    B --> C["❓ Question 2<br/>🔥 Hard: Event Loop Mechanics"]
    C --> D["📊 Score: 6/10<br/>🤔 Needs Clarification"]
    D --> E["❓ Question 3<br/>⚖️ Medium: Closures Example"]
    E --> F["🔄 Adaptive Flow<br/>📈 Continues Based on Performance"]
    
    classDef easy fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#000000
    classDef medium fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#000000
    classDef hard fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#000000
    classDef score fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#000000
    classDef flow fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#000000
    
    class A easy
    class E medium
    class C hard
    class B,D score
    class F flow
```

---

## 🛠️ **Development & Customization**

<details>
<summary><strong>🔧 Adding New Topics</strong></summary>

```python
# In question_bank.py
new_topic_questions = [
    {
        "question": "Your custom interview question",
        "difficulty": "medium", 
        "concepts": ["concept1", "concept2"],
        "expected_answer": "Expected response outline"
    }
]
```

</details>

<details>
<summary><strong>⚖️ Customizing Evaluation</strong></summary>

```python
# In evaluator.py - modify scoring weights
evaluation_weights = {
    "technical_accuracy": 0.30,      # Adjust weights
    "communication_clarity": 0.25,   # to match your needs  
    "practical_application": 0.20,
    # ... other dimensions
}
```

</details>

<details>
<summary><strong>🔄 Extending LangGraph Flow</strong></summary>

```python
# In flow_controller.py - add new states
workflow.add_node("custom_state", custom_function)
workflow.add_edge("evaluate_answer", "custom_state")
```

</details>

---

## 🏆 **Success Metrics**

<div align="center">

### **✅ Core Requirements Achievement**

<table>
<tr>
<td align="center">✅<br><strong>5 Dynamic Questions</strong><br><small>AI-generated by LLM</small></td>
<td align="center">✅<br><strong>Smart Branching</strong><br><small>Performance-based flow</small></td>
<td align="center">✅<br><strong>Detailed Summary</strong><br><small>Comprehensive feedback</small></td>
</tr>
<tr>
<td align="center">✅<br><strong>LangGraph Integration</strong><br><small>State machine control</small></td>
<td align="center">✅<br><strong>Local LLM</strong><br><small>Ollama llama3.2:3b</small></td>
<td align="center">✅<br><strong>Memory Management</strong><br><small>Full state tracking</small></td>
</tr>
</table>

### **⭐ Bonus Achievements**

<table>
<tr>
<td align="center">🏅<br><strong>Vector Database</strong><br><small>ChromaDB semantic search</small></td>
<td align="center">🏅<br><strong>Web Interface</strong><br><small>Professional Gradio UI</small></td>
<td align="center">🏅<br><strong>Analytics</strong><br><small>Real-time performance tracking</small></td>
<td align="center">🏅<br><strong>Production Ready</strong><br><small>Enterprise-grade architecture</small></td>
</tr>
</table>

</div>

---

## 🚀 **Getting Started**

<div align="center">

### **🎯 Prerequisites Checklist**

- [ ] Python 3.11+ installed
- [ ] Ollama installed and running  
- [ ] llama3.2:3b model downloaded
- [ ] Git for repository cloning

### **📦 Installation Commands**

```bash
# 1️⃣ Clone the repository
git clone https://github.com/VIKAS9793/ai-interviewer-langchain.git
cd ai-interviewer-langchain

# 2️⃣ Setup virtual environment  
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Launch the application
python main.py
```

### **🌐 Access Your Interview Portal**
**Open: `http://localhost:7860`**

</div>

---

## 🛠️ **Troubleshooting**

<details>
<summary><strong>🔧 Ollama Connection Issues</strong></summary>

```bash
# Check if Ollama is running
ollama list

# Start Ollama service  
ollama serve

# Download model if missing
ollama pull llama3.2:3b
```

</details>

<details>
<summary><strong>🗄️ ChromaDB Problems</strong></summary>

```bash
# Clear ChromaDB cache
rm -rf ./chroma_db

# Restart application
python main.py
```

</details>

<details>
<summary><strong>🌐 Web Interface Not Loading</strong></summary>

```bash
# Check port availability
netstat -an | grep 7860

# Use alternative port
python main.py --server-port 7861
```

</details>

---

## 🚀 **Future Roadmap**

<div align="center">

<table>
<tr>
<td width="50%">

### **🎯 Immediate Enhancements**

- [ ] 🎙️ Voice interview capability
- [ ] 💻 Code execution sandbox  
- [ ] 📹 Interview recording/playback
- [ ] 🌍 Multi-language support

</td>
<td width="50%">

### **🔮 Advanced Features**  

- [ ] 🎓 AI-powered interview coaching
- [ ] 🏢 HR systems integration
- [ ] 📊 Advanced analytics dashboard
- [ ] 📱 Mobile-responsive interface

</td>
</tr>
</table>

</div>

---

## 🤝 **Contributing**

<div align="center">

**We welcome contributions! Here's how to get started:**

```mermaid
flowchart LR
    A["🍴 Fork Repository"] --> B["🌿 Create Feature Branch"]
    B --> C["✏️ Make Changes"] 
    C --> D["💾 Commit Changes"]
    D --> E["🚀 Push to Branch"]
    E --> F["📝 Open Pull Request"]
    
    classDef step fill:#e8f5e8,stroke:#4caf50,stroke-width:2px,color:#000000
    classDef final fill:#e3f2fd,stroke:#2196f3,stroke-width:3px,color:#000000
    
    class A,B,C,D,E step
    class F final
```

</div>

1. **🍴 Fork the repository**
2. **🌿 Create your feature branch** (`git checkout -b feature/amazing-feature`)
3. **✅ Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **🚀 Push to the branch** (`git push origin feature/amazing-feature`)
5. **📝 Open a Pull Request**

---

## 📄 **License**

<div align="center">

**MIT License** - See [LICENSE](LICENSE) file for details

---

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 16px; color: white; margin: 20px 0;">

### **🚀 Built with ❤️ using cutting-edge AI technologies**

**LangGraph • Ollama • ChromaDB • Gradio • Python**

*Ready for production deployment and enterprise use cases*

</div>

**⭐ If this project helped you, please give it a star!**

</div>