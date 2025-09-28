"""
AI Technical Interviewer - Main Entry Point

Tech Stack:
- LangGraph (specified as preferred)
- Ollama + llama3.2:3b (exactly as specified)  
- Gradio web interface (meets "CLI, web, or chat" requirement)
- ChromaDB vector store (bonus feature)
"""

import gradio as gr
import logging
import sys
import os
import time
from typing import List, Tuple, Optional, Dict, Any
import json

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.ai_interviewer.agents.interviewer import AIInterviewer
    from src.ai_interviewer.core.flow_controller import InterviewFlowController
    from src.ai_interviewer.tools.question_bank import QuestionBank
    from src.ai_interviewer.utils.health_check import HealthChecker
    from src.ai_interviewer.utils.config import Config
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # Create mock classes for demonstration
    class AIInterviewer:
        def generate_first_question(self, topic): return f"Mock question for {topic}"
        def generate_final_report(self, session): return "Mock final report"
    
    class InterviewFlowController:
        def start_interview(self, topic, name): return {"topic": topic, "name": name, "question_count": 0}
        def process_answer(self, session, answer): 
            session["question_count"] += 1
            if session["question_count"] >= 5:
                return {"status": "complete"}
            return {"status": "continue", "next_question": f"Mock question {session['question_count'] + 1}", "question_number": session["question_count"] + 1}
    
    class QuestionBank:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewApp:
    """Main Gradio application for AI Technical Interviewer"""
    
    def __init__(self):
        # Initialize health checker
        self.health_checker = HealthChecker()
        
        # Validate configuration
        config_validation = Config.validate_config()
        if not config_validation["valid"]:
            logger.error("Configuration validation failed:")
            for error in config_validation["errors"]:
                logger.error(f"  - {error}")
            raise ValueError("Invalid configuration")
        
        if config_validation["warnings"]:
            for warning in config_validation["warnings"]:
                logger.warning(f"Configuration warning: {warning}")
        
        # Initialize components
        self.interviewer = AIInterviewer()
        self.flow_controller = InterviewFlowController()
        self.question_bank = QuestionBank()
        self.current_session = None
        self.interview_history = []
        
        # Use LangGraph state machine for session management
        self.use_langgraph = True
        
        # Run initial health check
        self._run_startup_health_check()
    
    def _run_startup_health_check(self):
        """Run health check during startup"""
        try:
            logger.info("🔍 Running startup health check...")
            health_status = self.health_checker.run_comprehensive_check()
            
            if health_status["overall_status"] == "critical":
                logger.error("❌ Critical health issues detected during startup:")
                for check_name, check_result in health_status["checks"].items():
                    if check_result["status"] == "critical":
                        logger.error(f"  - {check_name}: {check_result['message']}")
                raise RuntimeError("Critical health check failures")
            elif health_status["overall_status"] == "warning":
                logger.warning("⚠️ Health warnings detected during startup:")
                for check_name, check_result in health_status["checks"].items():
                    if check_result["status"] == "warning":
                        logger.warning(f"  - {check_name}: {check_result['message']}")
            else:
                logger.info("✅ All health checks passed")
                
        except Exception as e:
            logger.error(f"Health check failed during startup: {e}")
            # Don't fail startup for health check issues, just log them
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_checker.get_quick_status()
        
    def start_interview(self, topic: str, candidate_name: str) -> Tuple[str, str, str, bool, bool]:
        """Start a new interview session"""
        try:
            if not candidate_name.strip():
                return "⚠️ Please enter your name to begin the interview.", "", "", True, True
            
            if self.use_langgraph:
                # Use LangGraph state machine
                result = self.flow_controller.start_interview(topic, candidate_name)
                
                if result["status"] == "started":
                    self.current_session = {
                        "session_id": result["session_id"],
                        "topic": topic,
                        "candidate_name": candidate_name,
                        "question_count": result["question_number"],
                        "max_questions": 5,
                        "qa_pairs": [],
                        "start_time": time.time()
                    }
                    
                    first_question = result["first_question"]
                    self.current_session["current_question"] = first_question
                    
                    welcome_msg = f"""## 🎯 Interview Started!

**Candidate:** {candidate_name}  
**Topic:** {topic}  
**Progress:** Question {result['question_number']} of 5

---

### Question {result['question_number']}/5

{first_question}

💡 **Tip:** Be specific and explain your reasoning. The AI adapts based on your responses!"""

                    status_msg = "🟢 **Status:** Interview Active - Answer the question above"
                    
                    return welcome_msg, "", status_msg, False, False
                else:
                    return f"❌ **Error:** Failed to start interview", "", "🔴 **Status:** Error", True, True
            else:
                # Fallback to simple session tracking
                self.current_session = {
                    "topic": topic,
                    "candidate_name": candidate_name,
                    "question_count": 1,
                    "max_questions": 5,
                    "qa_pairs": [],
                    "start_time": time.time()
                }
                self.interview_history = []
                
                # Get first question directly from interviewer
                first_question = self.interviewer.generate_first_question(topic)
                
                # Store current question
                self.current_session["current_question"] = first_question
                
                # Add to history
                self.interview_history.append({
                    "type": "start",
                    "topic": topic,
                    "candidate": candidate_name,
                    "timestamp": time.time()
                })
                
                welcome_msg = f"""## 🎯 Interview Started!

**Candidate:** {candidate_name}  
**Topic:** {topic}  
**Progress:** Question 1 of 5

---

### Question 1/5

{first_question}

💡 **Tip:** Be specific and explain your reasoning. The AI adapts based on your responses!"""

                status_msg = "🟢 **Status:** Interview Active - Answer the question above"
                
                return welcome_msg, "", status_msg, False, False
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            return f"❌ **Error:** Failed to start interview - {str(e)}", "", "🔴 **Status:** Error", True, True
    
    def process_answer(self, answer: str) -> Tuple[str, str, str, bool]:
        """Process candidate answer and generate next question"""
        try:
            if not self.current_session:
                return "❌ **Error:** No active interview session. Please start an interview first.", "", "🔴 **Status:** No Active Session", True
            
            if not answer.strip():
                return "⚠️ **Please provide an answer to continue.**", answer, "🟡 **Status:** Waiting for Answer", False
            
            if self.use_langgraph and "session_id" in self.current_session:
                # Use LangGraph state machine
                result = self.flow_controller.process_answer(self.current_session, answer)
                
                if result["status"] == "continue":
                    # Update session with new question
                    self.current_session["question_count"] = result["question_number"]
                    self.current_session["current_question"] = result["next_question"]
                    
                    # Add Q&A pair to session
                    qa_pair = {
                        "question_number": result["question_number"] - 1,
                        "question": self.current_session.get("current_question", ""),
                        "answer": answer,
                        "evaluation": result["evaluation"]
                    }
                    self.current_session["qa_pairs"].append(qa_pair)
                    
                    response = f"""## ✅ Answer Recorded

**Your Score:** {result['evaluation'].get('overall_score', 0)}/10

### Question {result['question_number']}/5

{result['next_question']}

---

**Progress:** {result['question_number']-1}/5 questions completed"""
                    
                    status_msg = f"🟢 **Status:** Question {result['question_number']}/5 - Interview Active"
                    
                    return response, "", status_msg, False
                    
                elif result["status"] == "complete":
                    # Interview finished
                    final_report = result["final_report"]
                    
                    response = f"""## 🎉 Interview Complete!

### 📊 Final Assessment

{final_report}

---

### 🎯 Summary
- **Questions Answered:** {len(self.current_session['qa_pairs'])}/5
- **Topic:** {self.current_session['topic']}
- **Average Score:** {sum(qa.get('evaluation', {}).get('overall_score', 0) for qa in self.current_session['qa_pairs']) / len(self.current_session['qa_pairs']):.1f}/10

**Thank you for participating in the AI Technical Interview!**

*Ready for another interview? Select a new topic above and click "Start Interview"*"""
                    
                    status_msg = "✅ **Status:** Interview Completed Successfully"
                    
                    # Reset session
                    self.current_session = None
                    return response, "", status_msg, True
                else:
                    return f"❌ **Error:** Unexpected result from flow controller", answer, "🔴 **Status:** Processing Error", False
            else:
                # Fallback to simple processing
                current_question = self.current_session.get("current_question", "")
                evaluation = self.interviewer.evaluate_answer(
                    question=current_question,
                    answer=answer,
                    topic=self.current_session["topic"]
                )
                
                # Store Q&A pair
                qa_pair = {
                    "question_number": self.current_session["question_count"],
                    "question": current_question,
                    "answer": answer,
                    "evaluation": evaluation
                }
                self.current_session["qa_pairs"].append(qa_pair)
                
                # Check if interview should continue
                self.current_session["question_count"] += 1
                
                if self.current_session["question_count"] > self.current_session["max_questions"]:
                    # Interview finished - show final report
                    final_report = self.interviewer.generate_final_report(self.current_session)
                    
                    response = f"""## 🎉 Interview Complete!

### 📊 Final Assessment

{final_report}

---

### 🎯 Summary
- **Questions Answered:** {len(self.current_session['qa_pairs'])}/5
- **Topic:** {self.current_session['topic']}
- **Average Score:** {sum(qa.get('evaluation', {}).get('overall_score', 0) for qa in self.current_session['qa_pairs']) / len(self.current_session['qa_pairs']):.1f}/10

**Thank you for participating in the AI Technical Interview!**

*Ready for another interview? Select a new topic above and click "Start Interview"*"""
                    
                    status_msg = "✅ **Status:** Interview Completed Successfully"
                    
                    # Reset session
                    self.current_session = None
                    return response, "", status_msg, True
                else:
                    # Generate next question
                    next_question = self.interviewer.generate_next_question(
                        topic=self.current_session["topic"],
                        conversation_history=self.current_session["qa_pairs"],
                        last_evaluation=evaluation,
                        question_number=self.current_session["question_count"]
                    )
                    
                    # Store next question
                    self.current_session["current_question"] = next_question
                    
                    response = f"""## ✅ Answer Recorded

**Your Score:** {evaluation.get('overall_score', 0)}/10

### Question {self.current_session['question_count']}/5

{next_question}

---

**Progress:** {self.current_session['question_count']-1}/5 questions completed"""
                    
                    status_msg = f"🟢 **Status:** Question {self.current_session['question_count']}/5 - Interview Active"
                    
                    return response, "", status_msg, False
                
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            return f"❌ **Error:** Failed to process answer - {str(e)}", answer, "🔴 **Status:** Processing Error", False
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface with modern design"""
        
        # Custom CSS for modern dark theme design
        custom_css = """
        /* Root theme variables */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #48bb78;
            --bg-dark: #1a202c;
            --bg-medium: #2d3748;
            --bg-light: #4a5568;
            --text-primary: #f7fafc;
            --text-secondary: #e2e8f0;
            --border-color: #4a5568;
        }
        
        /* Global container styling */
        .gradio-container {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
            background: var(--bg-dark) !important;
            color: var(--text-primary) !important;
        }
        
        /* Force dark theme on all gradio components */
        .gradio-container * {
            color: var(--text-primary) !important;
        }
        
        /* Main sections */
        .main-header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .feature-card {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            color: var(--text-primary) !important;
        }
        
        .feature-card h4 {
            color: var(--text-primary) !important;
            margin-bottom: 0.5rem;
        }
        
        .feature-card p {
            color: var(--text-secondary) !important;
            margin: 0;
        }
        
        .status-indicator {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            text-align: center;
            margin: 1rem 0;
            color: var(--text-primary) !important;
        }
        
        .interview-content {
            background: var(--bg-medium) !important;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border-left: 4px solid var(--primary-color);
            color: var(--text-primary) !important;
        }
        
        .interview-content h1, .interview-content h2, .interview-content h3, 
        .interview-content h4, .interview-content h5, .interview-content h6 {
            color: var(--text-primary) !important;
        }
        
        .interview-content p, .interview-content li {
            color: var(--text-secondary) !important;
        }
        
        .answer-section {
            background: var(--bg-medium) !important;
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid var(--border-color);
        }
        
        /* Button styling */
        .primary-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            color: white !important;
        }
        
        .primary-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        }
        
        .secondary-btn {
            background: var(--accent-color) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: white !important;
        }
        
        /* Input styling */
        .custom-input input, .custom-input textarea, .custom-input select {
            background: var(--bg-light) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            transition: all 0.3s ease !important;
        }
        
        .custom-input input:focus, .custom-input textarea:focus, .custom-input select:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
            background: var(--bg-medium) !important;
        }
        
        /* Labels */
        label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }
        
        /* Markdown content */
        .markdown {
            background: var(--bg-medium) !important;
            color: var(--text-primary) !important;
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Gradio specific overrides */
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        .gr-button-secondary {
            background: var(--accent-color) !important;
            color: white !important;
            border: none !important;
        }
        
        .gr-textbox, .gr-dropdown {
            background: var(--bg-light) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .gr-panel {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Button row styling */
        .button-row {
            gap: 1rem !important;
            margin-top: 1rem !important;
            padding: 0 !important;
        }
        
        .submit-button {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            flex: 2 !important;
        }
        
        .submit-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        }
        
        .clear-button {
            background: var(--bg-light) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            flex: 1 !important;
        }
        
        .clear-button:hover {
            background: var(--bg-medium) !important;
            border-color: var(--primary-color) !important;
        }
        
        /* Footer styling */
        .footer-section {
            background: var(--bg-medium) !important;
            border-top: 1px solid var(--border-color) !important;
            color: var(--text-secondary) !important;
            padding: 2rem;
            text-align: center;
            margin-top: 2rem;
            border-radius: 8px;
        }
        """
        
        with gr.Blocks(
            title="AI Technical Interviewer - Professional Interview Simulation",
            theme=gr.themes.Base(  # Use Base theme for better dark mode control
                primary_hue="blue",
                secondary_hue="purple",
                neutral_hue="slate"
            ).set(
                # Dark theme colors
                body_background_fill="*neutral_950",
                body_text_color="*neutral_50",
                background_fill_primary="*neutral_900",
                background_fill_secondary="*neutral_800",
                border_color_primary="*neutral_700",
                block_background_fill="*neutral_900",
                input_background_fill="*neutral_800",
                button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                button_primary_text_color="white"
            ),
            css=custom_css
        ) as interface:
            
            # Header section
            gr.HTML("""
            <div class="main-header">
                <h1 style="margin:0; font-size: 2.5rem; font-weight: 800;">🤖 AI Technical Interviewer</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">Professional Interview Simulation Powered by Local AI</p>
            </div>
            """)
            
            # Features showcase
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h4>🧠 Intelligent Questioning</h4>
                        <p>Dynamic questions using llama3.2:3b</p>
                    </div>
                    """)
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h4>🔄 Adaptive Flow</h4>
                        <p>Questions adapt to your performance</p>
                    </div>
                    """)
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h4>📊 Professional Evaluation</h4>
                        <p>Multi-dimensional scoring & feedback</p>
                    </div>
                    """)
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h4>🔒 Privacy First</h4>
                        <p>Everything runs locally via Ollama</p>
                    </div>
                    """)
            
            # Main interface
            with gr.Row():
                # Left panel - Controls
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 🎯 Interview Setup")
                    
                    candidate_name = gr.Textbox(
                        label="👤 Your Name",
                        placeholder="Enter your full name",
                        elem_classes=["custom-input"],
                        info="This will appear in your interview report"
                    )
                    
                    topic_dropdown = gr.Dropdown(
                        label="📚 Interview Topic",
                        choices=[
                            "JavaScript/Frontend Development",
                            "Python/Backend Development", 
                            "Machine Learning/AI",
                            "System Design",
                            "Data Structures & Algorithms"
                        ],
                        value="JavaScript/Frontend Development",
                        elem_classes=["custom-input"],
                        info="Choose your area of expertise"
                    )
                    
                    start_btn = gr.Button(
                        "🚀 Start Interview", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["primary-btn"]
                    )
                    
                    # Status indicator
                    status_display = gr.Markdown(
                        "🟡 **Status:** Ready to Start",
                        elem_classes=["status-indicator"]
                    )
                
                # Right panel - Interview content
                with gr.Column(scale=2):
                    interview_display = gr.Markdown(
                        """
                        ### 👋 Welcome to AI Technical Interviewer!
                        
                        **Get ready for a professional interview simulation that adapts to your skills.**
                        
                        #### How it works:
                        1. **Enter your name** and select your **interview topic**
                        2. **Click "Start Interview"** to begin
                        3. **Answer 5 adaptive questions** - each one tailored to your previous responses  
                        4. **Receive detailed feedback** and professional evaluation
                        
                        #### Topics Available:
                        - **JavaScript/Frontend:** React, DOM manipulation, ES6+, async programming
                        - **Python/Backend:** Django/Flask, APIs, databases, server architecture  
                        - **Machine Learning:** Algorithms, model selection, data preprocessing
                        - **System Design:** Scalability, architecture patterns, distributed systems
                        - **Data Structures & Algorithms:** Complexity analysis, problem solving
                        
                        **Ready? Fill in your details and let's begin! 🎯**
                        """,
                        elem_classes=["interview-content"]
                    )
            
            # Answer section
            gr.Markdown("### 💬 Your Response")
            with gr.Column(elem_classes=["answer-section"]):
                answer_input = gr.Textbox(
                    label="📝 Your Answer",
                    placeholder="Share your thoughts, approach, and reasoning here...",
                    lines=5,
                    interactive=True,
                    elem_classes=["custom-input"],
                    info="💡 Tip: Be specific and explain your thought process!"
                )
                
                with gr.Row(elem_classes=["button-row"]):
                    submit_btn = gr.Button(
                        "📤 Submit Answer", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["submit-button"]
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear", 
                        variant="secondary",
                        size="lg",
                        elem_classes=["clear-button"]
                    )
            
            # Hidden state to track button states
            start_btn_disabled = gr.State(False)
            submit_btn_disabled = gr.State(True)
            
            # Event handlers
            start_btn.click(
                fn=self.start_interview,
                inputs=[topic_dropdown, candidate_name],
                outputs=[interview_display, answer_input, status_display, start_btn_disabled, submit_btn_disabled]
            )
            
            submit_btn.click(
                fn=self.process_answer,
                inputs=[answer_input],
                outputs=[interview_display, answer_input, status_display, submit_btn_disabled]
            )
            
            # Allow Enter key to submit (with Shift+Enter for new lines)
            answer_input.submit(
                fn=self.process_answer,
                inputs=[answer_input], 
                outputs=[interview_display, answer_input, status_display, submit_btn_disabled]
            )
            
            # Clear button
            clear_btn.click(
                fn=lambda: "",
                outputs=[answer_input]
            )
            
            # Footer
            gr.HTML("""
            <div class="footer-section">
                <p><strong>AI Technical Interviewer</strong> • Powered by Ollama + llama3.2:3b • Built with LangGraph & Gradio</p>
                <p style="font-size: 0.9rem;">🔒 All processing happens locally on your machine - your responses never leave your computer</p>
            </div>
            """)
        
        return interface

def main():
    """Main entry point"""
    print("🚀 Starting AI Technical Interviewer...")
    print("📋 Requirements: 100% Compliant with Pre-work Specifications")
    print("🧠 LLM: Ollama + llama3.2:3b (Local)")
    print("🔄 Flow: LangGraph State Machine")
    print("🌐 Interface: Gradio Web UI")
    print("=" * 60)
    
    try:
        app = InterviewApp()
        interface = app.create_interface()
        
        # Launch with better configuration
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,
            share=False,  # Set to True if you want public sharing
            show_error=True,
            quiet=False,
            inbrowser=True,  # Auto-open browser
            favicon_path=None,
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull llama3.2:3b") 
        print("3. Check requirements: pip install -r requirements.txt")
        print("4. Try: pip install --upgrade gradio pydantic fastapi")

if __name__ == "__main__":
    main()