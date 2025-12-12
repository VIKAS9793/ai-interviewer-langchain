"""
AI Technical Interviewer - Production-Grade Gradio UI
Clean Architecture | Responsive Design | Accessibility First
PATCHED FOR GRADIO 4.44 COMPATIBILITY
"""

import gradio as gr
import logging
import sys
import os
import time
import socket
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# Setup project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Ensure required directories exist
(project_root / "data" / "memory").mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules with graceful fallback
try:
    from src.ai_interviewer.core import AutonomousFlowController
    from src.ai_interviewer.core.ai_guardrails import ResponsibleAI
    from src.ai_interviewer.utils.config import Config
    from src.ai_interviewer.core.resume_parser import ResumeParser
    from src.ai_interviewer.security.scanner import SecurityScanner
    from src.ai_interviewer.utils.url_scraper import URLScraper
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some modules unavailable: {e}. Using fallback mode.")
    MODULES_AVAILABLE = False
    
    # Minimal fallback implementation
    class AutonomousFlowController:
        def __init__(self, **kwargs): pass
        def start_interview(self, topic, name, **kwargs): 
            return {
                "status": "started", 
                "session_id": "demo", 
                "first_question": f"What interests you about {topic}?",
                "greeting": f"Hello {name}! Let's begin."
            }
        def process_answer(self, session_id, answer): 
            return {
                "status": "continue",
                "next_question": "Great! Tell me more.",
                "question_number": 2,
                "evaluation": {"score": 7},
                "feedback": "Good response!",
                "reasoning": {"confidence": 0.8, "question_approach": "adaptive"}
            }
        def analyze_resume(self, text):
            return {"detected_role": "Software Engineer", "experience_level": "Mid"}

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

TOPICS = [
    "JavaScript/Frontend Development",
    "Python/Backend Development",
    "Machine Learning/AI",
    "System Design",
    "Data Structures & Algorithms",
    "Product Management",
    "DevOps/Cloud Engineering"
]

MAX_QUESTIONS = 5
DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

# ============================================================================
# THEME CONFIGURATION - Gradio 4.44 Compatible
# ============================================================================

# Import modular theme
from src.ui.styles.theme import create_theme, MINIMAL_CSS

# ============================================================================
# UI COMPONENT BUILDERS - Reusable, Pure Functions
# ============================================================================

# Import feedback components
from src.ui.components.feedback import (
    create_progress_display,
    format_question_display,
    format_feedback_display,
    format_final_report
)

# Import input components (reusable widgets)
from src.ui.components.inputs import (
    create_text_input,
    create_dropdown,
    create_file_upload,
    create_primary_button
)

# ============================================================================
# APPLICATION CLASS - Clean Separation of Concerns
# ============================================================================

class InterviewApplication:
    """Main application controller - handles business logic only"""
    
    def __init__(self):
        logger.info("🚀 Initializing AI Technical Interviewer...")
        
        self.flow_controller = AutonomousFlowController(
            max_concurrent_sessions=20,
            model_name=DEFAULT_MODEL
        )
        
        self.current_session: Optional[Dict[str, Any]] = None
        
        # Initialize speech recognition (optional)
        self._init_speech_recognition()
        
        logger.info("✅ Application initialized")
    
    def _init_speech_recognition(self):
        """Initialize speech recognition model (lazy loading)"""
        try:
            import whisper
            self.whisper_model = None  # Lazy load on first use
            self.speech_available = True
            logger.info("Speech recognition available (Whisper)")
        except ImportError:
            self.whisper_model = None
            self.speech_available = False
            logger.warning("Whisper not available - voice mode will use fallback")
    
    def transcribe_audio(self, audio_data) -> str:
        """Transcribe audio to text using Whisper"""
        if audio_data is None:
            return "⚠️ No audio recorded. Please record your answer first."
        
        try:
            # Lazy load Whisper model
            if self.whisper_model is None and self.speech_available:
                import whisper
                logger.info("Loading Whisper model (first use)...")
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper model loaded")
            
            if not self.speech_available:
                return "❌ Speech recognition not available. Please install: pip install openai-whisper"
            
            # Extract audio array
            sample_rate, audio_array = audio_data
            
            # Normalize audio to float32 [-1, 1]
            if audio_array.dtype != 'float32':
                audio_array = audio_array.astype('float32') / 32768.0
            
            # Whisper expects mono audio
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)
            
            # Transcribe
            result = self.whisper_model.transcribe(
                audio_array,
                language="en",
                fp16=False
            )
            
            transcription = result["text"].strip()
            
            if not transcription:
                return "⚠️ No speech detected. Please try recording again."
            
            return transcription
            
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return f"❌ Transcription failed: {str(e)}"
    
    # ========================================================================
    # INTERVIEW FLOW - Topic-Based
    # ========================================================================
    
    def start_topic_interview(
        self,
        topic: str,
        candidate_name: str
    ) -> Tuple:
        """Start topic-based interview"""
        
        # Validation
        if not candidate_name or not candidate_name.strip():
            return (
                "⚠️ Please enter your name to begin.",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),  # tabs visible
                gr.update(interactive=True),   # start enabled
                gr.update(interactive=True)    # practice enabled
            )
        
        try:
            # Start interview
            result = self.flow_controller.start_interview(
                topic=topic,
                candidate_name=candidate_name
            )
            
            if result["status"] != "started":
                error_msg = result.get('message', 'Failed to start interview')
                return (
                    f"❌ **Error:** {error_msg}",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Initialize session
            self.current_session = {
                "session_id": result["session_id"],
                "start_time": time.time(),
                "question_count": 1
            }
            
            # Format welcome message
            first_question = result.get("first_question", "Let's begin!")
            greeting = result.get("greeting", f"Welcome, {candidate_name}!")
            
            welcome_msg = f"""
# 👋 {greeting}

**Topic:** {topic}

{format_question_display(first_question, 1, MAX_QUESTIONS)}
"""
            
            progress = create_progress_display(1, 0)
            
            return (
                welcome_msg,
                progress,
                "",  # Clear answer box
                gr.update(visible=False), # Hide tabs
                gr.update(interactive=False), # Disable start
                gr.update(interactive=False)  # Disable practice
            )
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}", exc_info=True)
            return (
                f"❌ System Error: {str(e)}",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
    
    # ========================================================================
    # INTERVIEW FLOW - Practice Mode (Resume-based)
    # ========================================================================
    
    def start_practice_interview(
        self,
        resume_file,
        jd_text: str,
        jd_url: str,
        candidate_name: str
    ) -> Tuple:
        """Start practice mode with resume analysis"""
        
        # Validation
        if not candidate_name or not candidate_name.strip():
            return (
                "⚠️ Please enter your name first.",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
        
        if not resume_file:
            return (
                "⚠️ Please upload a resume to start Practice Mode.",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
        
        try:
            # Process resume
            if not MODULES_AVAILABLE:
                return (
                    "❌ Practice Mode requires full module installation.",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Get file path (Gradio 4.44 uses .name attribute)
            file_path = resume_file.name if hasattr(resume_file, 'name') else resume_file
            
            if not os.path.exists(file_path):
                return (
                    f"❌ File not found: {os.path.basename(file_path)}",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Security scan
            with open(file_path, 'rb') as f:
                is_safe, reason = SecurityScanner.scan_file(f, file_path)
            
            if not is_safe:
                return (
                    f"❌ Security Alert: {reason}",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Parse resume
            with open(file_path, 'rb') as f:
                resume_text = ResumeParser.extract_text(f, file_path)
            
            if not resume_text:
                return (
                    "❌ Could not extract text from resume. Please try a different format.",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Build context
            custom_context = {"resume_text": resume_text}
            
            # Process JD
            final_jd = ""
            if jd_url and jd_url.strip():
                scraped = URLScraper.extract_text(jd_url)
                if scraped:
                    final_jd += f"\n\n[From URL]: {scraped}"
            
            if jd_text and jd_text.strip():
                final_jd += f"\n\n[User Input]: {jd_text}"
            
            if final_jd:
                custom_context["job_description"] = final_jd
            
            # Analyze resume
            analysis = self.flow_controller.analyze_resume(resume_text)
            topic = analysis.get("detected_role", "Technical Interview")
            experience_level = analysis.get("experience_level", "Mid")
            
            custom_context["topic"] = topic
            custom_context["analysis"] = analysis
            
            # Start interview
            result = self.flow_controller.start_interview(
                topic, 
                candidate_name, 
                custom_context=custom_context
            )
            
            if result['status'] != 'started':
                return (
                    f"❌ Error: {result.get('message')}",
                    create_progress_display(0, 0),
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            # Initialize session
            self.current_session = {
                "session_id": result['session_id'],
                "topic": topic,
                "candidate_name": candidate_name,
                "question_count": 1,
                "start_time": time.time(),
                "mode": "practice"
            }
            
            # Format welcome
            skills = ', '.join(analysis.get('found_skills', [])[:5])
            
            welcome_msg = f"""
# 🎯 Practice Session Started

**Target Role:** {topic}  
**Experience Level:** {experience_level}  
**Detected Skills:** {skills}

---

{result.get('greeting', 'Welcome!')}

{format_question_display(result.get('first_question', ''), 1, MAX_QUESTIONS)}

---

> ℹ️ **Note:** This is a simulated interview based on your resume and the job description.
"""
            
            progress = create_progress_display(1, 0)
            
            return (
                welcome_msg,
                progress,
                "",
                gr.update(visible=False), # Hide tabs
                gr.update(interactive=False), # Disable start
                gr.update(interactive=False)  # Disable practice
            )
            
        except Exception as e:
            logger.error(f"Practice mode error: {e}", exc_info=True)
            return (
                f"❌ System Error: {str(e)}",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
    
    # ========================================================================
    # ANSWER PROCESSING
    # ========================================================================
    
    def process_answer(
        self,
        answer_text: str,
        transcription_text: str = ""
    ) -> Tuple:
        """Process candidate's answer (from either text or voice)"""
        
        # Check session
        if not self.current_session:
            return (
                "❌ No active session. Please start an interview first.",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
        
        # Use transcription if provided, otherwise text input
        final_answer = transcription_text if transcription_text else answer_text
        
        # Validate input
        if not final_answer or not final_answer.strip():
            elapsed = int(time.time() - self.current_session["start_time"])
            q_num = self.current_session["question_count"]
            return (
                "⚠️ Please provide an answer before submitting.",
                create_progress_display(q_num, elapsed),
                final_answer,  # Keep existing text
                gr.update(visible=False),
                gr.update(interactive=True), # Keep enabled to retry
                gr.update(interactive=False) # Practice disabled
            )
        
        try:
            # Process with AI
            result = self.flow_controller.process_answer(
                self.current_session["session_id"],
                final_answer
            )
            
            elapsed = int(time.time() - self.current_session["start_time"])
            
            # Handle continuation
            if result["status"] == "continue":
                self.current_session["question_count"] = result.get("question_number", 2)
                
                evaluation = result.get("evaluation", {})
                feedback = result.get("feedback", "")
                next_question = result.get("next_question", "")
                reasoning = result.get("reasoning", {})
                q_num = result.get("question_number", 2)
                
                display = format_feedback_display(
                    evaluation.get("score", 5),
                    feedback,
                    next_question,
                    q_num,
                    reasoning
                )
                
                progress = create_progress_display(q_num, elapsed)
                
                return (
                    display,
                    progress,
                    "",  # Clear answer
                    gr.update(visible=False),
                    gr.update(interactive=True), # Enable for next question
                    gr.update(interactive=False)
                )
            
            # Handle completion
            elif result["status"] == "completed":
                summary = result.get("summary", {})
                
                display = format_final_report(summary, elapsed)
                progress = create_progress_display(MAX_QUESTIONS, elapsed)
                
                self.current_session = None
                
                return (
                    display,
                    progress,
                    "",
                    gr.update(visible=True),
                    gr.update(interactive=True),
                    gr.update(interactive=True)
                )
            
            else:
                return (
                    f"❌ Error: {result.get('message', 'Unexpected error')}",
                    create_progress_display(0, elapsed),
                    final_answer,
                    gr.update(visible=False),
                    gr.update(interactive=True), # Enable to retry
                    gr.update(interactive=False)
                )
                
        except Exception as e:
            logger.error(f"Error processing answer: {e}", exc_info=True)
            return (
                f"❌ System Error: {str(e)}",
                create_progress_display(0, 0),
                final_answer,
                gr.update(visible=True), # Recover
                gr.update(interactive=True),
                gr.update(interactive=True)
            )

# Import UI Builder
from src.ui.app import create_interface

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def is_port_available(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

def main():
    """Application entry point"""
    print("=" * 80)
    print("AI Technical Interviewer")
    print("=" * 80)
    print(f"Python: {sys.version}")
    print(f"Gradio: {gr.__version__}")
    print(f"Project Root: {project_root}")
    print("=" * 80)
    
    try:
        # Initialize application
        app = InterviewApplication()
        
        # Create interface
        interface = create_interface(app)
        
        # Configure for production
        interface.queue(
            default_concurrency_limit=10,
            max_size=20
        )
        
        # Launch with hardcoded port for HF Spaces stability
        print(f"\n🚀 Launching application on port 7860...")
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\n📋 Troubleshooting:")
        print("1. Check HF_TOKEN environment variable")
        print("2. Verify all dependencies: pip install -r requirements.txt")
        print("3. Check system resources and port availability")
        sys.exit(1)

if __name__ == "__main__":
    main()