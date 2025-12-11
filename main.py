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
    from src.ai_interviewer.core.resume_parser import ResumeParser
    from src.ai_interviewer.security.scanner import SecurityScanner
    from src.ai_interviewer.utils.url_scraper import URLScraper
    AUTONOMOUS_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import autonomous modules: {e}")
    AUTONOMOUS_SYSTEM_AVAILABLE = False
    
    # Minimal fallback
    class AutonomousFlowController:
        def __init__(self, **kwargs):
            pass
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
        
        # Ensure data directories exist
        import os
        os.makedirs("data/memory", exist_ok=True)
        
        # Fix: Ensure Gradio cache directory exists (HuggingFace Spaces fix)
        # See: https://huggingface.co/docs/hub/spaces-sdks-gradio
        gradio_cache = os.environ.get("GRADIO_TEMP_DIR", "/tmp/gradio")
        os.makedirs(gradio_cache, exist_ok=True)
        os.environ["GRADIO_TEMP_DIR"] = gradio_cache
        
        # Initialize autonomous flow controller
        self.flow_controller = AutonomousFlowController(
            max_concurrent_sessions=20,
            model_name="meta-llama/Meta-Llama-3-8B-Instruct"
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
    
    # --- Code Smell Fix: Extracted helper methods for button states ---
    @staticmethod
    def _buttons_enabled():
        """Return tuple to enable both start buttons and show tabs (reduces duplicate code)"""
        return gr.update(interactive=True), gr.update(interactive=True), gr.update(visible=True)
    
    @staticmethod
    def _buttons_disabled():
        """Return tuple to disable both start buttons and hide tabs during interview"""
        return gr.update(interactive=False), gr.update(interactive=False), gr.update(visible=False)
    
    def _format_reasoning_display(self, reasoning: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
        """Format AI reasoning for display in the Accordion"""
        approach = reasoning.get('question_approach', 'adaptive').replace('_', ' ').title()
        confidence = reasoning.get('confidence', 0.7)
        thought_chain_id = reasoning.get('thought_chain_id', 'N/A')
        
        # Get grounding info from evaluation
        grounding = evaluation.get('grounding', {})
        accuracy = grounding.get('accuracy_assessment', 'unverified')
        correct_points = grounding.get('correct_points', [])
        missing_concepts = grounding.get('missing_concepts', [])
        
        # Build grounding section
        grounding_section = ""
        if grounding:
            grounding_icon = "✅" if accuracy == "verified" else "⚠️"
            grounding_section = f"""
---

#### 📚 Knowledge Grounding {grounding_icon}

**Verification Status:** {accuracy.replace('_', ' ').title()}
"""
            if correct_points:
                grounding_section += "\n**Verified Concepts:**\n"
                for point in correct_points[:3]:
                    grounding_section += f"- ✓ {point.get('concept', '').replace('_', ' ').title()}\n"
            
            if missing_concepts:
                grounding_section += "\n**Consider mentioning:**\n"
                for concept in missing_concepts[:2]:
                    grounding_section += f"- 💡 {concept.replace('_', ' ').title()}\n"
        
        # Build reasoning markdown
        md = f"""### 🧠 AI Decision Process

**Reasoning Chain ID:** {thought_chain_id}

---

#### 📊 Evaluation Metrics
| Metric | Value |
|--------|-------|
| **Approach** | {approach} |
| **Confidence** | {confidence:.0%} |
| **Score Given** | {evaluation.get('score', 5)}/10 |

---

#### 💭 Chain of Thought
1. **Analyzed** candidate's response for technical accuracy
2. **Evaluated** depth, clarity, and practical understanding
3. **Compared** against expert-level benchmarks
4. **Selected** {approach} strategy for next question
5. **Confidence** level: {confidence:.0%} based on response quality
{grounding_section}
---

*Powered by Autonomous Reasoning Engine + Knowledge Grounding*
"""
        return md
    
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
    
    def _generate_progress_html(self, question_num: int = 0, elapsed_seconds: int = 0, start_timestamp: float = 0) -> str:
        """Generate progress bar HTML with elapsed time (updates on each interaction)"""
        progress_pct = (question_num / 5) * 100 if question_num > 0 else 0
        
        # Calculate elapsed from start_timestamp if available
        if start_timestamp > 0 and question_num > 0:
            import time
            elapsed_seconds = int(time.time() - start_timestamp)
        
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Note: Gradio sanitizes JavaScript, so timer updates only on each interaction
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
        
    def _start_practice_mode(self, resume_file, jd_text, jd_url, candidate_name):
        """
        Handle Practice Mode initialization:
        1. Scan/Parse Resume
        2. Fetch JD
        3. Analyze Context
        4. Start Interview
        """
        try:
            if not candidate_name or not candidate_name.strip():
                return "⚠️ Please enter your name first.", "", self._generate_progress_html(0, 0), "waiting", *self._buttons_enabled()
                
            custom_context = {}
            
            # --- 1. Process Resume ---
            if resume_file:
                # Gradio 5 compatibility: file can be string path or file object
                import os
                if isinstance(resume_file, str):
                    file_path = resume_file
                elif hasattr(resume_file, 'name'):
                    file_path = resume_file.name
                else:
                    file_path = str(resume_file)
                
                # Validate file exists
                if not os.path.exists(file_path):
                    return f"❌ File not found: {os.path.basename(file_path)}. Please re-upload.", "", self._generate_progress_html(0, 0), "file_error", *self._buttons_enabled()
                
                # Security Scan
                with open(file_path, 'rb') as f:
                    is_safe, refusal_reason = SecurityScanner.scan_file(f, file_path)
                
                if not is_safe:
                     return f"❌ Security Alert: {refusal_reason}", "", self._generate_progress_html(0, 0), "security_block", *self._buttons_enabled()
                
                # Parse
                with open(file_path, 'rb') as f:
                    resume_text = ResumeParser.extract_text(f, file_path)
                
                if not resume_text:
                    return "❌ Failed to extract text from resume.", "", self._generate_progress_html(0, 0), "parse_error", *self._buttons_enabled()
                    
                custom_context["resume_text"] = resume_text
            else:
                return "⚠️ Please upload a resume to start Practice Mode.", "", self._generate_progress_html(0, 0), "waiting", *self._buttons_enabled()

            # --- 2. Process Job Description ---
            final_jd_text = ""
            if jd_url and jd_url.strip():
                scraped_text = URLScraper.extract_text(jd_url)
                if scraped_text:
                    final_jd_text += f"\n\n[From URL]: {scraped_text}"
            
            if jd_text and jd_text.strip():
                final_jd_text += f"\n\n[User Input]: {jd_text}"
                
            if final_jd_text:
                custom_context["job_description"] = final_jd_text
            
            # --- 3. Analyze & Start ---
            # Analyze resume to determine topic/level if not explicit
            analysis = self.flow_controller.analyze_resume(custom_context["resume_text"])
            
            # Determine topic from resume analysis or JD
            topic = analysis.get("detected_role", "General Technical Interview")
            experience_level = analysis.get("experience_level", "Mid")
            
            # If JD is provided, try to extract role from it
            if "job_description" in custom_context:
                jd_lower = custom_context["job_description"].lower()
                # Simple JD role extraction
                if "product manager" in jd_lower:
                    topic = "Product Management"
                elif "software engineer" in jd_lower:
                    topic = "Software Engineering"
                elif "data scientist" in jd_lower:
                    topic = "Data Science"
            
            custom_context["topic"] = topic
            custom_context["analysis"] = analysis
            
            # Start
            result = self.flow_controller.start_interview(topic, candidate_name, custom_context=custom_context)
            
            if result['status'] == 'started':
                import time as time_module
                self.current_session = {
                    "session_id": result['session_id'],
                    "start_time": time_module.time(),
                    "question_count": 1
                }
                self.interview_history = []
                
                # Format Welcome Message
                welcome_msg = f"""### 🎯 Practice Session Started
                
**Target Role:** {topic}
**Experience Level:** {experience_level}
**Candidate:** {candidate_name}

**Analysis:**
*   **Skills Detected:** {', '.join(analysis.get('found_skills', []))}

> ⚠️ **Beta Notice:** Evaluation scoring is optimized for technical interviews. Business/PM interview evaluation improvements coming in v3.0 with Gemini integration.

{result.get('greeting', 'Hello!')}

{result.get('first_question', 'Ready to begin?')}
"""
                return welcome_msg, "", self._generate_progress_html(1, 0), "Status: In Progress", *self._buttons_disabled()

            else:
                 return f"Error: {result.get('message')}", "", self._generate_progress_html(0, 0), "error", *self._buttons_enabled()

        except Exception as e:
            logger.error(f"Practice Mode Error: {e}")
            return f"System Error: {str(e)}", "", self._generate_progress_html(0, 0), "error", *self._buttons_enabled()
    def start_interview(self, topic: str, candidate_name: str, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct") -> Tuple[str, str, str, str, bool, bool]:
        """Start autonomous interview session with self-thinking AI"""
        try:
            if not candidate_name.strip():
                return "WARN Please enter your name to begin the interview.", "", self._generate_progress_html(0, 0), "", *self._buttons_enabled()
            
            # Force Single-Model Architecture (Ignore UI input which is now a display label)
            model_id = Config.DEFAULT_MODEL
            
            # Set model on flow controller's interviewer
            if hasattr(self.flow_controller, 'interviewer'):
                self.flow_controller.interviewer.set_model(model_id)
            
            # Start autonomous interview
            result = self.flow_controller.start_interview(topic, candidate_name)
            
            if result["status"] == "started":
                # Get model display name
                model_names = {
                    "meta-llama/Meta-Llama-3-8B-Instruct": "LLaMA 3 (8B)",
                    "mistralai/Mistral-7B-Instruct-v0.3": "Mistral (7B)",
                    "meta-llama/Meta-Llama-3-8B-Instruct": "LLaMA 3 (8B)"
                }
                model_display = model_names.get(model_id, model_id.split("/")[-1])
                
                self.current_session = {
                    "session_id": result["session_id"],
                    "topic": topic,
                    "candidate_name": candidate_name,
                    "model_id": model_id,
                    "model_display": model_display,
                    "question_count": 1,
                    "max_questions": 5,
                    "qa_pairs": [],
                    "start_time": time.time()
                }
                
                first_question = result.get("first_question", "")
                greeting = result.get("greeting", f"Welcome, {candidate_name}!")
                
                # Enhanced welcome with autonomous features
                welcome_msg = f"""## Autonomous AI Interview Started!

**Candidate:** {candidate_name}  
**Topic:** {topic}  
**AI Model:** {model_display}

### {greeting}

---

### Autonomous Features Active:
- **Self-Thinking:** Chain-of-Thought reasoning before every action
- **Logical Reasoning:** Multi-step analysis of your responses
- **Self-Resilient:** Graceful error recovery
- **Human-Like:** Natural, adaptive conversation
- **AI Guardrails:** Fair, unbiased, explainable decisions
- **Accountability:** Complete audit trail

---

### Question 1/5

{first_question}

INFO **The AI thinks before asking each question and explains its reasoning!**"""

                status_msg = f"🟢 **Status:** Autonomous Interview Active - Question 1/5"
                progress_html = self._generate_progress_html(1, 0, self.current_session["start_time"])
                
                return welcome_msg, "", progress_html, status_msg, *self._buttons_disabled()
            else:
                error_msg = result.get('message', 'Failed to start interview')
                return f"❌ **Error:** {error_msg}", "", self._generate_progress_html(0, 0), "🔴 **Status:** Error", *self._buttons_enabled()
            
        except Exception as e:
            logger.error(f"Error starting autonomous interview: {e}")
            return f"❌ **Error:** {str(e)}", "", self._generate_progress_html(0, 0), "🔴 **Status:** Error", *self._buttons_enabled()
    
    def process_answer(self, answer_text: str, answer_code: str, mode: str = "Text Answer") -> Tuple[str, str, str, str, bool, str]:
        """Process answer with autonomous reasoning and guardrails"""
        try:
            # Determine which input to use
            answer = answer_code if mode == "Code Editor" else answer_text
            
            if not self.current_session:
                return "❌ **Error:** No active session. Please start an interview.", "", self._generate_progress_html(0, 0), "🔴 **Status:** No Session", True, ""
            
            if not answer or not answer.strip():
                elapsed = int(time.time() - self.current_session.get("start_time", time.time()))
                q_num = self.current_session.get("question_count", 1)
                start_ts = self.current_session.get("start_time", 0)
                return "⚠️ **Please provide an answer.**", answer, self._generate_progress_html(q_num, elapsed, start_ts), "🟡 **Status:** Waiting", False, ""
            
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
                start_ts = self.current_session.get("start_time", 0)
                progress_html = self._generate_progress_html(q_num, elapsed, start_ts)
                
                # Generate reasoning markdown for Accordion
                reasoning_md = self._format_reasoning_display(reasoning, evaluation)
                
                return response, "", progress_html, status_msg, False, reasoning_md
                
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
                return response, "", self._generate_progress_html(5, elapsed), "✅ **Status:** Interview Completed", True, ""
            else:
                return f"❌ **Error:** {result.get('message', 'Unexpected error')}", answer, self._generate_progress_html(0, elapsed), "🔴 **Status:** Error", False, ""
            
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            return f"❌ **Error:** {str(e)}", answer, self._generate_progress_html(0, 0), "🔴 **Status:** Error", False, ""
    
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
            border: 1px solid var(--border-color) !important;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Space Grotesk', sans-serif;
            font-variant-numeric: tabular-nums;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .timer-icon {
            font-size: 1.1rem;
            animation: pulse 2s infinite;
        }
        
        .timer-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--primary-light) !important;
        }

        /* Fix Radio Button Contrast - High Specificity */
        .gradio-container fieldset {
            background: transparent !important;
        }
        
        /* Target the Radio Group Wrapper */
        .gradio-container .block.form {
            background: var(--bg-medium) !important;
            border-color: var(--border-color) !important;
        }

        /* Target ALL radio option labels */
        .gradio-container .wrap label span {
            color: #E2E8F0 !important; /* Force light hex for safety */
            font-weight: 500;
        }
        
        /* Specifically target unselected radio buttons */
        .gradio-container label:not(.selected) span {
            color: #CBD5E1 !important; /* Slightly dimmer white */
        }
        
        /* Ensure checked state is also visible */
        .gradio-container label.selected span {
            color: #FFFFFF !important;
            font-weight: 700;
        }
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
            css=enhanced_css,
            fill_width=True  # UI: Maximize screen utilization
        ) as interface:
            
            # Header (Simple & Clean)
            gr.HTML(
                '<div class="enhanced-header">'
                '<h1 style="margin:0; font-size: 2.5rem; font-weight: 800;">AI Technical Interviewer</h1>'
                '<p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Single-Model Architecture | Chain-of-Thought Reasoning | Voice Mode</p>'
                '</div>'
            )
            
            # --- Tabbed Interface (Clean & Focused) ---
            # Wrap in Column for visibility control (gr.Tabs doesn't support visible)
            with gr.Column() as tabs_container:
                with gr.Tabs() as mode_tabs:
                
                    # --- TAB 1: Topic Interview ---
                    with gr.Tab("Technical Interviewer"):
                        with gr.Row():
                            with gr.Column(scale=1, min_width=300):
                                candidate_name = gr.Textbox(
                                    label="Name",
                                    placeholder="Candidate Name",
                                    elem_classes=["custom-input"]
                                )
                                
                                topic_dropdown = gr.Dropdown(
                                    label="Topic",
                                    choices=[
                                        "JavaScript/Frontend Development",
                                        "Python/Backend Development", 
                                        "Machine Learning/AI",
                                        "System Design",
                                        "Data Structures & Algorithms"
                                    ],
                                    value="JavaScript/Frontend Development",
                                    elem_classes=["custom-input"]
                                )
                                
                                start_btn = gr.Button(
                                    "Start Interview", 
                                    variant="primary", 
                                    size="lg",
                                    elem_classes=["enhanced-btn"]
                                )
                
                    # --- TAB 2: Practice Mode ---
                    with gr.Tab("Practice Mode"):
                        gr.Markdown("#### Resume & JD Simulation")
                        
                        with gr.Row():
                            with gr.Column():
                                practice_name = gr.Textbox(
                                    label="Name",
                                    placeholder="Candidate Name",
                                    elem_classes=["custom-input"]
                                )
                                
                                resume_upload = gr.File(
                                    label="Resume (PDF/DOCX)",
                                    file_types=[".pdf", ".docx"],
                                    file_count="single",
                                    elem_classes=["custom-input"]
                                )
                            
                            with gr.Column():
                                jd_url = gr.Textbox(
                                    label="JD URL",
                                    placeholder="https://...",
                                    elem_classes=["custom-input"]
                                )
                                
                                jd_text = gr.Textbox(
                                    label="Or Paste JD",
                                    placeholder="Job Description Text...",
                                    lines=3,
                                    elem_classes=["custom-input"]
                                )
                        
                        start_practice_btn = gr.Button(
                            "Analyze & Start Practice", 
                            variant="primary", 
                            size="lg",
                            elem_classes=["enhanced-btn"]
                        )

            # --- Two-Column Interview Layout (v2.6) ---
            with gr.Row():
                # LEFT COLUMN - Question & Progress (40%)
                with gr.Column(scale=2, min_width=350):
                    # Compact status bar
                    with gr.Row():
                        system_status = gr.Markdown(
                            "🟡 **Ready** | ⏱ 00:00 | Q: 0/5",
                            elem_classes=["compact-status"]
                        )
                    
                    # Progress bar
                    progress_html = gr.HTML(
                        """
                        <div class="progress-container" style="padding: 0.5rem 0;">
                            <div class="progress-bar-wrapper" style="height: 8px; border-radius: 4px; background: #334155;">
                                <div class="progress-bar-fill" style="width: 0%; height: 100%; border-radius: 4px; background: linear-gradient(90deg, #667eea, #9f7aea);"></div>
                            </div>
                        </div>
                        """,
                        elem_id="progress-tracker"
                    )
                    
                    # Question display
                    interview_display = gr.Markdown(
                        "### AI Technical Interviewer\n\n**Powered by Meta LLaMA 3 (8B)**\n\n#### Instructions\n1. **Setup**: Enter name & topic (or upload resume)\n2. **Start**: Click the launch button\n3. **Speak**: Use Voice Mode for hands-free",
                        elem_classes=["enhanced-interview-content"]
                    )
                
                # RIGHT COLUMN - Answer (60%)
                with gr.Column(scale=3, min_width=400):
                    # Hidden reasoning (for results only)
                    reasoning_display = gr.Markdown(
                        "",
                        visible=False,
                        elem_classes=["reasoning-display"]
                    )
                    
                    # Answer section
                    gr.Markdown("### 💬 Your Response")
                    with gr.Column(elem_classes=["answer-section"]):
                        # Voice Mode Toggle (v2.4)
                        voice_mode = gr.Radio(
                            choices=["Text", "Voice 🎤"],
                            value="Text",
                            label="Input Mode",
                            info="Use Voice for hands-free input (Chrome/Edge/Safari)"
                        )
                        
                        # Voice Controls (Hidden by default) - Using HTML buttons with inline JS
                        with gr.Row(visible=False) as voice_controls:
                            voice_control_html = gr.HTML('''
                            <script>
                            // Voice Mode v2.4 - Inline Script (ensures functions exist before buttons)
                            (function() {
                                // Rate limiting
                                let lastVoiceInput = 0;
                                const RATE_LIMIT_MS = 3000;
                                const MAX_TRANSCRIPT_LENGTH = 2000;
                                
                                // Check browser support
                                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                                if (!SpeechRecognition) {
                                    console.warn('Voice Mode: Speech Recognition not supported');
                                    window.startVoiceRecording = function() { alert('Voice not supported in this browser. Please use Chrome or Edge.'); };
                                    window.stopVoiceRecording = function() {};
                                    return;
                                }
                                
                                // Initialize recognition
                                const recognition = new SpeechRecognition();
                                recognition.continuous = false;
                                recognition.interimResults = false;
                                recognition.lang = 'en-US';
                                
                                // Sanitize input
                                function sanitize(text) {
                                    if (!text) return '';
                                    return text.replace(/<[^>]+>/g, '').replace(/(javascript:|on\w+=)/gi, '').substring(0, MAX_TRANSCRIPT_LENGTH).trim();
                                }
                                
                                // Start listening
                                window.startVoiceRecording = function() {
                                    const now = Date.now();
                                    if (now - lastVoiceInput < RATE_LIMIT_MS) {
                                        alert('Please wait a few seconds before recording again.');
                                        return;
                                    }
                                    lastVoiceInput = now;
                                    
                                    
                                    const status = document.getElementById('voice-status');
                                    if (status) {
                                        status.innerHTML = 'DOT <strong>Listening...</strong> Speak now';
                                        status.style.background = 'rgba(239, 68, 68, 0.2)';
                                    }
                                    
                                    try {
                                        recognition.start();
                                    } catch (e) {
                                        console.error('Recognition start error:', e);
                                        if (status) status.innerHTML = 'WARN Error starting - try again';
                                    }
                                };
                                
                                // Stop listening
                                window.stopVoiceRecording = function() {
                                    recognition.stop();
                                    const status = document.getElementById('voice-status');
                                    if (status) {
                                        status.innerHTML = 'READY Ready to record';
                                        status.style.background = 'rgba(34, 197, 94, 0.2)';
                                    }
                                };
                                
                                // Handle result
                                recognition.onresult = function(event) {
                                    const transcript = sanitize(event.results[0][0].transcript);
                                    const confidence = event.results[0][0].confidence;
                                    
                                    // Find Gradio textbox and update it
                                    const textbox = document.querySelector('#answer-textbox textarea');
                                    if (textbox) {
                                        textbox.value = transcript;
                                        textbox.dispatchEvent(new Event('input', { bubbles: true }));
                                    }
                                    
                                    const status = document.getElementById('voice-status');
                                    if (status) {
                                        status.innerHTML = 'OK Transcribed (' + Math.round(confidence * 100) + '% confidence)';
                                        status.style.background = 'rgba(34, 197, 94, 0.2)';
                                    }
                                };
                                
                                // Handle errors
                                recognition.onerror = function(event) {
                                    console.error('Speech error:', event.error);
                                    const status = document.getElementById('voice-status');
                                    if (status) {
                                        status.innerHTML = 'WARN ' + event.error + ' - Try again or use text';
                                        status.style.background = 'rgba(245, 158, 11, 0.2)';
                                    }
                                };
                                
                                recognition.onend = function() {
                                    const status = document.getElementById('voice-status');
                                    if (status && !status.innerHTML.includes('OK')) {
                                        status.innerHTML = 'READY Ready to record';
                                        status.style.background = 'rgba(34, 197, 94, 0.2)';
                                    }
                                };
                                
                                console.log('Voice Mode v2.4 ready');
                            })();
                            </script>
                            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap; padding: 10px;">
                                <div id="voice-status" style="padding: 10px 20px; border-radius: 8px; background: rgba(34, 197, 94, 0.2); text-align: center; flex: 1;">
                                    READY Click microphone to start
                                </div>
                                <button onclick="window.startVoiceRecording()" style="padding: 10px 20px; border-radius: 8px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; cursor: pointer; font-size: 1rem; font-weight: 600;">
                                    Start Recording
                                </button>
                                <button onclick="window.stopVoiceRecording()" style="padding: 10px 20px; border-radius: 8px; background: #4b5563; color: white; border: none; cursor: pointer; font-size: 1rem;">
                                    Stop
                                </button>
                                <label style="display: flex; align-items: center; gap: 5px; color: var(--text-primary);">
                                    <input type="checkbox" id="speak-response-checkbox" checked style="width: 18px; height: 18px;">
                                    Speak Response
                                </label>
                            </div>
                            ''')
                        
                        # Input Mode Selection - DISABLED (v2.3 Rollback)
                        input_mode = gr.Radio(
                            choices=["Text Answer", "Code Editor"],
                            value="Text Answer",
                            label="Input Mode",
                            info="Code Editor temporarily disabled likely due to Cloud API limits",
                            visible=False, 
                            interactive=False
                        )

                        answer_input = gr.Textbox(
                            label="📝 Your Answer",
                            placeholder="Share your thoughts, approach, and reasoning here...",
                            lines=5,
                            interactive=True,
                            elem_classes=["custom-input"],
                            elem_id="answer-textbox",
                            info="💡 Voice Mode: Click 🎤 to speak your answer!"
                        )
                        
                        code_input = gr.Code(
                            value="",
                            language="python",
                            label="💻 Code Editor",
                            interactive=False,
                            visible=False
                        )
                        
                        # Input toggle logic
                        def toggle_input(mode):
                            if mode == "Code Editor":
                                return gr.update(visible=False), gr.update(visible=True)
                            else:
                                return gr.update(visible=True), gr.update(visible=False)

                        input_mode.change(
                            fn=toggle_input,
                            inputs=[input_mode],
                            outputs=[answer_input, code_input]
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
            
            # Clear Inputs Helper
            def clear_inputs():
                return "", ""
            
            # Tab 1: Topic Interview
            start_btn.click(
                fn=self.start_interview,
                inputs=[topic_dropdown, candidate_name],
                outputs=[interview_display, answer_input, progress_html, system_status, start_btn, start_practice_btn, tabs_container]
            )
            
            # Tab 2: Practice Mode
            start_practice_btn.click(
                fn=self._start_practice_mode,
                inputs=[resume_upload, jd_text, jd_url, practice_name],
                outputs=[interview_display, answer_input, progress_html, system_status, start_btn, start_practice_btn, tabs_container]
            )
            
            # Handle Enter key on Textbox
            answer_input.submit(
                fn=self.process_answer,
                inputs=[answer_input, code_input, input_mode],
                outputs=[interview_display, answer_input, progress_html, system_status, start_btn, reasoning_display]
            ).then(
                fn=clear_inputs,
                outputs=[answer_input, code_input]
            )
            
            # Input Toggle (Disabled v2.3)
            input_mode.change(
                fn=toggle_input,
                inputs=[input_mode],
                outputs=[answer_input, code_input]
            )
            
            submit_btn.click(
                fn=self.process_answer,
                inputs=[answer_input, code_input, input_mode],
                outputs=[interview_display, answer_input, progress_html, system_status, submit_btn_disabled, reasoning_display]
            )
            
            # Clear button
            
            clear_btn.click(
                fn=clear_inputs,
                outputs=[answer_input, code_input]
            )
            
            # Enhanced footer
            # Enhanced footer
            gr.HTML(
                '<div class="footer-section">'
                '<p><strong>Enhanced AI Technical Interviewer</strong> | Autonomous Learning System | Powered by Advanced AI Agents</p>'
                '<p style="font-size: 0.9rem;">Chain-of-Thought Reasoning | Semantic Evaluation | Hybrid Scoring | AI Guardrails | Voice Mode</p>'
                '<p style="font-size: 0.8rem;">Built with LangChain, HuggingFace Inference API, Gradio, and Sentence Transformers</p>'
                '</div>'
            )
            
            # Voice Mode Toggle Logic
            def toggle_voice_mode(mode):
                if "Voice" in mode:
                    return gr.update(visible=True)
                else:
                    return gr.update(visible=False)
            
            voice_mode.change(
                fn=toggle_voice_mode,
                inputs=[voice_mode],
                outputs=[voice_controls]
            )
        
        return interface

def main():
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
        
        # Detect Gradio version for compatibility
        import gradio
        gradio_version = tuple(map(int, gradio.__version__.split('.')[:2]))
        is_gradio_5 = gradio_version >= (5, 0)
        print(f"Detected Gradio version: {gradio.__version__} (v5+: {is_gradio_5})")
        
        try:
            # Queue for Spaces - default_concurrency_limit for Gradio 4.x
            interface.queue(default_concurrency_limit=2)
            
            # Build launch args conditionally
            launch_args = {
                "server_name": "0.0.0.0",
                "server_port": 7860,
                "share": False,
                "show_error": True,
                "quiet": False,
            }
            # Add Gradio 5.x specific args only if supported
            if is_gradio_5:
                launch_args["ssr_mode"] = False
            
            interface.launch(**launch_args)
        except Exception as launch_error:
            print(f"Failed to launch on port {available_port}: {launch_error}")
            print("Attempting to find another available port...")
            
            # Try alternative ports
            for alt_port in range(available_port + 1, available_port + 10):
                if is_port_available(alt_port):
                    print(f"Trying alternative port: {alt_port}")
                    try:
                        alt_launch_args = {
                            "server_name": "0.0.0.0",
                            "server_port": alt_port,
                            "share": False,
                            "show_error": True,
                            "quiet": False,
                            "inbrowser": False,
                            "favicon_path": None,
                        }
                        if is_gradio_5:
                            alt_launch_args["ssr_mode"] = False
                        interface.launch(**alt_launch_args)
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
        print("\nTroubleshooting (Cloud Deployment):")
        print("1. Ensure HF_TOKEN is set: export HF_TOKEN=your_token")
        print("2. Check requirements: pip install -r requirements.txt")
        print("3. Verify HuggingFace API status: https://status.huggingface.co")
        print("4. Try: pip install --upgrade gradio langchain-huggingface")
        print("5. Check system resources and network connectivity")
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
