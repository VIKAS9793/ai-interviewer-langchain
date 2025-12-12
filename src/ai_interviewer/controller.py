import logging
import time
import os
import gradio as gr
from typing import Tuple, Optional, Any, Dict

from src.ai_interviewer.utils.config import Config
from src.ui.components.feedback import (
    create_progress_display,
    format_question_display,
    format_feedback_display,
    format_final_report
)

# Configure logging
logger = logging.getLogger(__name__)

# Import modules with graceful fallback
try:
    from src.ai_interviewer.core import AutonomousFlowController
    from src.ai_interviewer.core.ai_guardrails import ResponsibleAI
    from src.ai_interviewer.core.resume_parser import ResumeParser
    from src.ai_interviewer.security.scanner import SecurityScanner
    from src.ai_interviewer.utils.url_scraper import URLScraper
    from src.ai_interviewer.modules.jd_parser import JDParser, parse_job_description
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some modules unavailable: {e}. Using fallback mode.")
    MODULES_AVAILABLE = False
    
    # Minimal fallback implementation
    class AutonomousFlowController:
        def __init__(self, **kwargs): pass
        def start_interview(self, topic, candidate_name, **kwargs): 
            return {
                "status": "started", 
                "session_id": "demo", 
                "first_question": f"What interests you about {topic}?",
                "greeting": f"Hello {candidate_name}! Let's begin."
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

class InterviewApplication:
    """
    Main application controller.
    Manages interview state, coordinates between UI and AI logic,
    and handles session persistence.
    """
    
    def __init__(self):
        # Initialize Core Logic
        self.flow_controller = AutonomousFlowController(
            model_name=Config.DEFAULT_MODEL,
            temperature=Config.MODEL_TEMPERATURE
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

{format_question_display(first_question, 1, Config.MAX_QUESTIONS)}
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
            
            # Process JD with intelligent parsing
            final_jd = ""
            jd_role = None
            jd_company = None
            
            # Parse JD URL for role extraction
            if jd_url and jd_url.strip():
                jd_info = parse_job_description(url=jd_url)
                jd_role = jd_info.get("role_title")
                jd_company = jd_info.get("company_name")
                
                # Also scrape full text for context
                scraped = URLScraper.extract_text(jd_url)
                if scraped:
                    final_jd += f"\n\n[From URL]: {scraped}"
                    
                    # Parse scraped text for more details
                    text_info = parse_job_description(text=scraped)
                    if not jd_role:
                        jd_role = text_info.get("role_title")
                    if not jd_company:
                        jd_company = text_info.get("company_name")
                    custom_context["jd_requirements"] = text_info.get("requirements", [])
            
            if jd_text and jd_text.strip():
                final_jd += f"\n\n[User Input]: {jd_text}"
                # Parse pasted text
                text_info = parse_job_description(text=jd_text)
                if not jd_role:
                    jd_role = text_info.get("role_title")
                if not jd_company:
                    jd_company = text_info.get("company_name")
                if not custom_context.get("jd_requirements"):
                    custom_context["jd_requirements"] = text_info.get("requirements", [])
            
            if final_jd:
                custom_context["job_description"] = final_jd
            
            # Analyze resume
            analysis = self.flow_controller.analyze_resume(resume_text)
            resume_skills = analysis.get("skills", [])
            experience_level = analysis.get("experience_level", "Mid")
            
            # Determine topic: JD role > resume detected role > fallback
            if jd_role:
                topic = jd_role
                logger.info(f"🎯 Using JD role: {topic}")
            else:
                topic = analysis.get("detected_role") or analysis.get("suggested_topics", ["Technical Interview"])[0]
                logger.info(f"🎯 Using resume-detected role: {topic}")
            
            # Add company context if available
            if jd_company:
                custom_context["company_name"] = jd_company
                logger.info(f"🏢 Company detected: {jd_company}")
            
            custom_context["topic"] = topic
            custom_context["target_role"] = topic
            custom_context["resume_skills"] = resume_skills
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

{format_question_display(result.get('first_question', ''), 1, Config.MAX_QUESTIONS)}

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
                progress = create_progress_display(Config.MAX_QUESTIONS, elapsed)
                
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
