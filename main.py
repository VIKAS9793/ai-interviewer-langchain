"""
Enhanced AI Technical Interviewer - Main Entry Point
Autonomous Self-Thinking, Responsible AI Interview System
"""

import gradio as gr
import logging
import sys
import os
import time
import asyncio
import socket
from typing import List, Tuple, Optional, Dict, Any
import json
from pathlib import Path

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def find_available_port(start_port: int = 7860, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

def is_port_available(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

# Import new Autonomous AI System
try:
    from src.ai_interviewer.core import AutonomousFlowController
    from src.ai_interviewer.core.ai_guardrails import ResponsibleAI
    from src.ai_interviewer.utils.config import Config
    AUTONOMOUS_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import autonomous modules: {e}")
    AUTONOMOUS_SYSTEM_AVAILABLE = False
    
    # Minimal fallback
    class AutonomousFlowController:
        def start_interview(self, topic, name): 
            return {"status": "started", "session_id": "fallback", "first_question": f"Fallback question for {topic}", "greeting": f"Welcome {name}!"}
        def process_answer(self, session_id, answer): 
            return {"status": "continue", "next_question": "Fallback next question", "question_number": 2, "evaluation": {"score": 5}, "feedback": "Good attempt"}
        def get_system_status(self):
            return {"status": "fallback"}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedInterviewApp:
    """Autonomous AI Technical Interviewer with Self-Thinking Capabilities"""
    
    def __init__(self):
        """Initialize with new autonomous system"""
        logger.info("🚀 Initializing Autonomous AI Interviewer...")
        
        # Initialize autonomous flow controller
        self.flow_controller = AutonomousFlowController(
            max_concurrent_sessions=20,
            model_name="llama3.2:3b"
        )
        
        # Initialize ResponsibleAI guardrails
        if AUTONOMOUS_SYSTEM_AVAILABLE:
            self.responsible_ai = ResponsibleAI()
        else:
            self.responsible_ai = None
        
        self.current_session = None
        self.interview_history = []
        
        # Autonomous features
        self.autonomous_features = {
            "self_thinking": True,
            "logical_reasoning": True,
            "self_resilient": True,
            "human_like_conduct": True,
            "ai_guardrails": True,
            "explainability": True,
            "accountability": True
        }
        
        logger.info("✅ Autonomous AI Interviewer initialized")
        logger.info(f"   Autonomous features: {list(self.autonomous_features.keys())}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        system_status = self.flow_controller.get_system_status()
        
        return {
            "system_status": system_status.get("status", "operational"),
            "autonomous_features": self.autonomous_features,
            "performance": system_status.get("performance", {}),
            "capacity": system_status.get("capacity", {}),
            "responsible_ai": {
                "guardrails_active": self.responsible_ai is not None,
                "compliance": self.responsible_ai.get_compliance_status() if self.responsible_ai else {}
            }
        }
    
    def _generate_progress_html(self, question_num: int = 0, elapsed_seconds: int = 0) -> str:
        """Generate progress bar HTML with current state"""
        progress_pct = (question_num / 5) * 100 if question_num > 0 else 0
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        return f"""
        <div class="progress-container">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">Question</span>
                <span style="color: var(--learning-color); font-weight: 600;">{question_num} / 5</span>
            </div>
            <div class="progress-bar-wrapper">
                <div class="progress-bar-fill" style="width: {progress_pct}%;">{question_num}/5</div>
            </div>
        </div>
        <div class="timer-display">
            <span class="timer-icon">⏱️</span>
            <span style="color: var(--text-secondary);">Elapsed:</span>
            <span class="timer-value">{time_str}</span>
        </div>
        """
        
    def start_interview(self, topic: str, candidate_name: str) -> Tuple[str, str, str, str, bool, bool]:
        """Start autonomous interview session with self-thinking AI"""
        try:
            if not candidate_name.strip():
                return "⚠️ Please enter your name to begin the interview.", "", self._generate_progress_html(0, 0), "", True, True
            
            # Start autonomous interview
            result = self.flow_controller.start_interview(topic, candidate_name)
            
            if result["status"] == "started":
                self.current_session = {
                    "session_id": result["session_id"],
                    "topic": topic,
                    "candidate_name": candidate_name,
                    "question_count": 1,
                    "max_questions": 5,
                    "qa_pairs": [],
                    "start_time": time.time()
                }
                
                first_question = result.get("first_question", "")
                greeting = result.get("greeting", f"Welcome, {candidate_name}!")
                
                # Enhanced welcome with autonomous features
                welcome_msg = f"""## 🤖 Autonomous AI Interview Started!

**Candidate:** {candidate_name}  
**Topic:** {topic}

### {greeting}

---

### 🧠 Autonomous Features Active:
- **🤔 Self-Thinking:** Chain-of-Thought reasoning before every action
- **📊 Logical Reasoning:** Multi-step analysis of your responses
- **💪 Self-Resilient:** Graceful error recovery
- **🎭 Human-Like:** Natural, adaptive conversation
- **🛡️ AI Guardrails:** Fair, unbiased, explainable decisions
- **📋 Accountability:** Complete audit trail

---

### Question 1/5

{first_question}

💡 **The AI thinks before asking each question and explains its reasoning!**"""

                status_msg = f"🟢 **Status:** Autonomous Interview Active - Question 1/5"
                progress_html = self._generate_progress_html(1, 0)
                
                return welcome_msg, "", progress_html, status_msg, False, False
            else:
                error_msg = result.get('message', 'Failed to start interview')
                return f"❌ **Error:** {error_msg}", "", self._generate_progress_html(0, 0), "🔴 **Status:** Error", True, True
            
        except Exception as e:
            logger.error(f"Error starting autonomous interview: {e}")
            return f"❌ **Error:** {str(e)}", "", self._generate_progress_html(0, 0), "🔴 **Status:** Error", True, True
    
    def process_answer(self, answer: str) -> Tuple[str, str, str, str, bool]:
        """Process answer with autonomous reasoning and guardrails"""
        try:
            if not self.current_session:
                return "❌ **Error:** No active session. Please start an interview.", "", self._generate_progress_html(0, 0), "🔴 **Status:** No Session", True
            
            if not answer.strip():
                elapsed = int(time.time() - self.current_session.get("start_time", time.time()))
                q_num = self.current_session.get("question_count", 1)
                return "⚠️ **Please provide an answer.**", answer, self._generate_progress_html(q_num, elapsed), "🟡 **Status:** Waiting", False
            
            # Validate content with guardrails
            if self.responsible_ai:
                content_check = self.responsible_ai.validate_content(answer)
                if not content_check.get("safe", True):
                    logger.warning(f"Content flagged: {content_check.get('issues', [])}")
            
            # Process with autonomous system
            result = self.flow_controller.process_answer(
                self.current_session["session_id"], 
                answer
            )
            
            # Calculate elapsed time
            elapsed = int(time.time() - self.current_session.get("start_time", time.time()))
            
            if result["status"] == "continue":
                # Update session
                self.current_session["question_count"] = result.get("question_number", 2)
                
                evaluation = result.get("evaluation", {})
                feedback = result.get("feedback", "")
                reasoning = result.get("reasoning", {})
                q_num = result.get('question_number', 2)
                
                response = f"""## ✅ Answer Evaluated with Autonomous Reasoning

**Your Score:** {evaluation.get('score', 5)}/10

### 🧠 AI Reasoning:
- **Approach Used:** {reasoning.get('question_approach', 'adaptive').replace('_', ' ').title()}
- **Confidence:** {reasoning.get('confidence', 0.7):.0%}
- **Candidate State:** {result.get('candidate_state', 'neutral').title()}

### 💬 Feedback:
{feedback}

---

### Question {q_num}/5

{result.get('next_question', '')}"""

                status_msg = f"🟢 **Status:** Autonomous - Question {q_num}/5"
                progress_html = self._generate_progress_html(q_num, elapsed)
                return response, "", progress_html, status_msg, False
                
            elif result["status"] == "completed":
                final_report = result.get("final_report", "Interview completed.")
                summary = result.get("summary", {})
                
                # Format elapsed time
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes}m {seconds}s"
                
                response = f"""## 🎉 Autonomous Interview Complete!

{final_report}

---

### 📊 Performance Summary:
- **Questions:** {summary.get('questions_asked', 5)}
- **Average Score:** {summary.get('avg_score', 0):.1f}/10
- **Total Time:** {time_str}
- **Strengths:** {', '.join(summary.get('strengths', ['N/A'])[:3])}
- **Areas to Improve:** {', '.join(summary.get('areas_for_improvement', ['N/A'])[:3])}

### 🤖 Autonomous AI Insights:
- **Thought Chains Used:** {result.get('autonomous_insights', {}).get('thought_chains_used', 0)}
- **Adaptations Made:** {result.get('autonomous_insights', {}).get('adaptations_made', 0)}

**Ready for another interview? Select a topic and click Start!**"""

                self.current_session = None
                return response, "", self._generate_progress_html(5, elapsed), "✅ **Status:** Interview Completed", True
            else:
                return f"❌ **Error:** {result.get('message', 'Unexpected error')}", answer, self._generate_progress_html(0, elapsed), "🔴 **Status:** Error", False
            
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            return f"❌ **Error:** {str(e)}", answer, self._generate_progress_html(0, 0), "🔴 **Status:** Error", False
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        try:
            return self.flow_controller.get_learning_analytics()
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}

    def create_enhanced_interface(self) -> gr.Blocks:
        """Create enhanced Gradio interface with adaptive features"""
        
        # Enhanced CSS for modern design
        enhanced_css = """
        /* Enhanced theme variables */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #48bb78;
            --learning-color: #9f7aea;
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
        
        /* Enhanced header */
        .enhanced-header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #9f7aea 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        /* Learning features showcase */
        .learning-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .learning-feature {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .learning-feature:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(159, 122, 234, 0.3);
        }
        
        .learning-feature h4 {
            color: var(--learning-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .learning-feature p {
            color: var(--text-secondary) !important;
            margin: 0;
            font-size: 0.9rem;
        }
        
        /* Performance indicators */
        .performance-indicator {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .performance-indicator .label {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        .performance-indicator .value {
            color: var(--accent-color) !important;
            font-weight: 700;
        }
        
        /* Enhanced interview content */
        .enhanced-interview-content {
            background: var(--bg-medium) !important;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border-left: 4px solid var(--learning-color);
            color: var(--text-primary) !important;
        }
        
        /* Learning insights panel */
        .learning-insights {
            background: var(--bg-light) !important;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid var(--learning-color);
        }
        
        .learning-insights h4 {
            color: var(--learning-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .learning-insights p {
            color: var(--text-secondary) !important;
            margin: 0.25rem 0;
        }
        
        /* Enhanced buttons */
        .enhanced-btn {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--learning-color) 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            color: white !important;
        }
        
        .enhanced-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(159, 122, 234, 0.4) !important;
        }
        
        /* System status indicator */
        .system-status {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .system-status h4 {
            color: var(--accent-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .system-status .status-item {
            display: flex;
            justify-content: space-between;
            margin: 0.25rem 0;
        }
        
        .system-status .status-label {
            color: var(--text-secondary) !important;
        }
        
        .system-status .status-value {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        /* Progress bar styling */
        .progress-container {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .progress-bar-wrapper {
            background: var(--bg-dark);
            border-radius: 20px;
            height: 24px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--learning-color) 100%);
            border-radius: 20px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        /* Timer styling */
        .timer-display {
            background: var(--bg-medium) !important;
            border: 1px solid var(--learning-color) !important;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .timer-icon {
            font-size: 1.2rem;
        }
        
        .timer-value {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--learning-color) !important;
            font-family: 'Courier New', monospace;
        }
        """
        
        with gr.Blocks(
            title="Enhanced AI Technical Interviewer - Autonomous Learning System",
            theme=gr.themes.Base(
                primary_hue="blue",
                secondary_hue="purple",
                neutral_hue="slate"
            ).set(
                body_background_fill="*neutral_950",
                body_text_color="*neutral_50",
                background_fill_primary="*neutral_900",
                background_fill_secondary="*neutral_800",
                border_color_primary="*neutral_700",
                block_background_fill="*neutral_900",
                input_background_fill="*neutral_800",
                button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #9f7aea 100%)",
                button_primary_text_color="white"
            ),
            css=enhanced_css
        ) as interface:
            
            # Enhanced header
            gr.HTML("""
            <div class="enhanced-header">
                <h1 style="margin:0; font-size: 2.5rem; font-weight: 800;">🧠 Enhanced AI Technical Interviewer</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">Autonomous Learning-Based Adaptive Intelligence System</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.8;">Powered by Advanced AI Agents & Offline Optimization</p>
            </div>
            """)
            
            # Learning features showcase
            gr.HTML("""
            <div class="learning-features">
                <div class="learning-feature">
                    <h4>🧠 Adaptive Learning</h4>
                    <p>System learns from each interview and improves over time</p>
                </div>
                <div class="learning-feature">
                    <h4>📊 Performance Analysis</h4>
                    <p>Real-time difficulty adjustment based on performance</p>
                </div>
                <div class="learning-feature">
                    <h4>🎯 Knowledge Tracking</h4>
                    <p>Identifies strengths and knowledge gaps automatically</p>
                </div>
                <div class="learning-feature">
                    <h4>⚡ Offline Optimization</h4>
                    <p>Cached responses and optimized performance</p>
                </div>
                <div class="learning-feature">
                    <h4>🔄 Concurrent Processing</h4>
                    <p>Handles multiple interviews simultaneously</p>
                </div>
                <div class="learning-feature">
                    <h4>🔒 Privacy First</h4>
                    <p>Everything runs locally with advanced security</p>
                </div>
            </div>
            """)
            
            # Main interface
            with gr.Row():
                # Left panel - Controls
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 🎯 Enhanced Interview Setup")
                    
                    candidate_name = gr.Textbox(
                        label="👤 Your Name",
                        placeholder="Enter your full name",
                        elem_classes=["custom-input"],
                        info="This will appear in your enhanced interview report"
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
                        "🚀 Start Enhanced Interview", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["enhanced-btn"]
                    )
                    
                    # System status
                    gr.Markdown("### 📊 Interview Progress")
                    
                    # Progress bar HTML component
                    progress_html = gr.HTML(
                        """
                        <div class="progress-container">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: var(--text-secondary);">Question</span>
                                <span style="color: var(--learning-color); font-weight: 600;">0 / 5</span>
                            </div>
                            <div class="progress-bar-wrapper">
                                <div class="progress-bar-fill" style="width: 0%;"></div>
                            </div>
                        </div>
                        <div class="timer-display">
                            <span class="timer-icon">⏱️</span>
                            <span style="color: var(--text-secondary);">Elapsed:</span>
                            <span class="timer-value">00:00</span>
                        </div>
                        """,
                        elem_id="progress-tracker"
                    )
                    
                    system_status = gr.Markdown(
                        "🟡 **Status:** Ready to Start",
                        elem_classes=["system-status"]
                    )
                
                # Right panel - Interview content
                with gr.Column(scale=2):
                    interview_display = gr.Markdown(
                        """
                        ### 👋 Welcome to Enhanced AI Technical Interviewer!
                        
                        **Experience the future of AI-powered interviews with autonomous learning capabilities.**
                        
                        #### 🧠 How Enhanced Learning Works:
                        1. **Enter your name** and select your **interview topic**
                        2. **Click "Start Enhanced Interview"** to begin
                        3. **Answer 5 adaptive questions** - each one intelligently tailored to your responses
                        4. **Receive comprehensive feedback** with learning insights and recommendations
                        
                        #### 🚀 Enhanced Features:
                        - **🧠 Adaptive Learning:** System learns from every interview and improves
                        - **📊 Performance Analysis:** Real-time difficulty adjustment based on your performance
                        - **🎯 Knowledge Tracking:** Automatically identifies your strengths and knowledge gaps
                        - **⚡ Offline Optimization:** Cached responses for faster, more efficient processing
                        - **🔄 Concurrent Processing:** Handles multiple interviews simultaneously
                        - **🔒 Privacy First:** Everything runs locally on your machine
                        
                        #### 📚 Available Topics:
                        - **JavaScript/Frontend:** React, DOM manipulation, ES6+, async programming
                        - **Python/Backend:** Django/Flask, APIs, databases, server architecture  
                        - **Machine Learning:** Algorithms, model selection, data preprocessing
                        - **System Design:** Scalability, architecture patterns, distributed systems
                        - **Data Structures & Algorithms:** Complexity analysis, problem solving
                        
                        **Ready to experience the future of AI interviews? Let's begin! 🎯**
                        """,
                        elem_classes=["enhanced-interview-content"]
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
                    info="💡 Enhanced Tip: The AI analyzes your response patterns and adapts accordingly!"
                )
                
                with gr.Row(elem_classes=["button-row"]):
                    submit_btn = gr.Button(
                        "📤 Submit Answer", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["enhanced-btn"]
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
                outputs=[interview_display, answer_input, progress_html, system_status, start_btn_disabled, submit_btn_disabled]
            )
            
            submit_btn.click(
                fn=self.process_answer,
                inputs=[answer_input],
                outputs=[interview_display, answer_input, progress_html, system_status, submit_btn_disabled]
            )
            
            # Allow Enter key to submit
            answer_input.submit(
                fn=self.process_answer,
                inputs=[answer_input], 
                outputs=[interview_display, answer_input, progress_html, system_status, submit_btn_disabled]
            )
            
            # Clear button
            clear_btn.click(
                fn=lambda: "",
                outputs=[answer_input]
            )
            
            # Enhanced footer
            gr.HTML("""
            <div class="footer-section">
                <p><strong>Enhanced AI Technical Interviewer</strong> • Autonomous Learning System • Powered by Advanced AI Agents</p>
                <p style="font-size: 0.9rem;">🧠 Learning Intelligence • ⚡ Offline Optimization • 🔄 Concurrent Processing • 🔒 Privacy First</p>
                <p style="font-size: 0.8rem;">Built with LangGraph, Ollama + llama3.2:3b, ChromaDB, and Advanced Caching</p>
            </div>
            """)
        
        return interface

def main():
    """Enhanced main entry point"""
    print("Starting Enhanced AI Technical Interviewer...")
    print("Features: Autonomous Learning-Based Adaptive Intelligence")
    print("Requirements: 100% Compliant with Enterprise Standards")
    print("LLM: Hugging Face Cloud (Meta-Llama-3-8B-Instruct)")
    print("Flow: Enhanced LangGraph with Learning")
    print("Optimization: Cloud Caching & Concurrency")
    print("Interface: Enhanced Gradio Web UI")
    print("=" * 80)
    
    try:
        app = EnhancedInterviewApp()
        interface = app.create_enhanced_interface()
        
        # Find an available port dynamically
        try:
            available_port = find_available_port(start_port=7860, max_attempts=20)
            print(f"Found available port: {available_port}")
        except RuntimeError as e:
            print(f"Port finding failed: {e}")
            print("Falling back to default port 7860...")
            available_port = 7860
        
        # Launch with enhanced configuration and dynamic port
        print(f"Launching Enhanced AI Interviewer on port {available_port}...")
        
        try:
            # Queue for Spaces - default_concurrency_limit for Gradio 4.x
            interface.queue(default_concurrency_limit=2)
            
            interface.launch(
                server_name="0.0.0.0",  # Allow external access
                server_port=7860,  # Fixed port for Spaces
                share=False,  # Disabled for Spaces (platform handles this)
                show_error=True,
                quiet=False,
            )
        except Exception as launch_error:
            print(f"Failed to launch on port {available_port}: {launch_error}")
            print("Attempting to find another available port...")
            
            # Try alternative ports
            for alt_port in range(available_port + 1, available_port + 10):
                if is_port_available(alt_port):
                    print(f"Trying alternative port: {alt_port}")
                    try:
                        interface.launch(
                            server_name="0.0.0.0",
                            server_port=alt_port,
                            share=False,  # Disabled for Spaces
                            show_error=True,
                            quiet=False,
                            inbrowser=False,  # Disabled for Spaces
                            favicon_path=None,
                        )
                        print(f"Successfully launched on port {alt_port}")
                        break
                    except Exception as alt_error:
                        print(f"Port {alt_port} also failed: {alt_error}")
                        continue
            else:
                raise RuntimeError("Could not find any available port to launch the application")
        
    except Exception as e:
        logger.error(f"Failed to start enhanced application: {e}")
        print(f"Error: {e}")
        print("\nEnhanced Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull llama3.2:3b")
        print("3. Check requirements: pip install -r requirements.txt")
        print("4. Try: pip install --upgrade gradio pydantic fastapi")
        print("5. Check system resources for concurrent processing")
        print("6. Try running on a different port manually")
        
        # Try to find and suggest available ports
        print("\nChecking for available ports...")
        for port in range(7860, 7870):
            if is_port_available(port):
                print(f"Port {port} is available")
            else:
                print(f"Port {port} is occupied")

if __name__ == "__main__":
    main()
