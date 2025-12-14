import logging
import time
import os
import gradio as gr
from typing import Tuple, Optional, Any, Dict

from src.ai_interviewer.utils.config import Config
from src.ai_interviewer.utils.input_validator import InputValidator


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
        if Config.LANGGRAPH_ENABLED:
            try:
                from src.ai_interviewer.core.interview_graph import InterviewGraph
                self.flow_controller = InterviewGraph()
                logger.info("🔷 Using LangGraph Engine (v3.1)")
            except ImportError as e:
                logger.error(f"Failed to load LangGraph: {e}. Falling back to Legacy Controller.")
                self.flow_controller = AutonomousFlowController(
                    model_name=Config.DEFAULT_MODEL,
                    temperature=Config.MODEL_TEMPERATURE
                )
        else:
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
            import whisper  # type: ignore[reportMissingImports]  # Optional dependency
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
                import whisper  # type: ignore[reportMissingImports]  # Optional dependency
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
            
            # Enforce length limit
            is_valid, error_msg = InputValidator.validate_voice_transcript(transcription)
            if not is_valid:
                logger.warning(f"Voice transcript exceeded limit: {len(transcription)} chars")
                # Truncate to limit
                max_len = Config.VOICE_MAX_TRANSCRIPT_LENGTH
                transcription = transcription[:max_len]
                return f"⚠️ Transcription truncated (max {max_len} characters). {transcription}"
            
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
    ) -> Dict[str, Any]:
        """Start topic-based interview (Returns Data Dict)"""
        
        # Input validation
        is_valid, error_msg = InputValidator.validate_name(candidate_name)
        if not is_valid:
            return {"success": False, "message": error_msg or "Please enter your name to begin."}
        
        try:
            # Start interview
            result = self.flow_controller.start_interview(
                topic=topic,
                candidate_name=candidate_name
            )
            
            if result["status"] != "started":
                return {"success": False, "message": result.get('message', 'Failed to start interview')}
            
            # Initialize session
            self.current_session = {
                "session_id": result["session_id"],
                "start_time": time.time(),
                "question_count": 1
            }
            
            return {
                "success": True,
                "session_id": result["session_id"],
                "greeting": result.get("greeting", f"Welcome, {candidate_name}!"),
                "first_question": result.get("first_question", "Let's begin!"),
                "question_number": 1,
                "total_questions": Config.MAX_QUESTIONS,
                "topic": topic
            }
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}", exc_info=True)
            is_production = os.getenv("ENVIRONMENT") == "production"
            safe_message = InputValidator.sanitize_error_message(e, is_production)
            return {"success": False, "message": safe_message}
    
    # ========================================================================
    # INTERVIEW FLOW - Practice Mode (Resume-based)
    # ========================================================================
    
    def start_practice_interview(
        self,
        resume_file,
        jd_text: str,
        jd_url: str,
        candidate_name: str
    ) -> Dict[str, Any]:
        """Start practice mode (Returns Data Dict)"""
        
        # Input validation
        is_valid, error_msg = InputValidator.validate_name(candidate_name)
        if not is_valid:
            return {"success": False, "message": error_msg or "Please enter your name first."}
        
        if not resume_file:
            return {"success": False, "message": "Please upload a resume to start Practice Mode."}
        
        # Validate JD text if provided
        if jd_text:
            is_valid, error_msg = InputValidator.validate_jd_text(jd_text)
            if not is_valid:
                return {"success": False, "message": error_msg}
        
        # Validate JD URL if provided
        if jd_url:
            is_valid, error_msg = InputValidator.validate_url(jd_url)
            if not is_valid:
                return {"success": False, "message": f"Invalid URL: {error_msg}"}
        
        try:
            # Process resume
            if not MODULES_AVAILABLE:
                return {"success": False, "message": "Practice Mode requires full module installation."}
            
            # Get file path (Gradio 4.44 uses .name attribute)
            file_path = resume_file.name if hasattr(resume_file, 'name') else resume_file
            
            if not os.path.exists(file_path):
                return {"success": False, "message": f"File not found: {os.path.basename(file_path)}"}
            
            # Security scan
            with open(file_path, 'rb') as f:
                is_safe, reason = SecurityScanner.scan_file(f, file_path)
            
            if not is_safe:
                return {"success": False, "message": f"Security Alert: {reason}"}
            
            # Parse resume
            with open(file_path, 'rb') as f:
                resume_text = ResumeParser.extract_text(f, file_path)
            
            if not resume_text:
                return {"success": False, "message": "Could not extract text from resume."}
            
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
                # Extract proper interview context (core role + specific area)
                interview_context = JDParser.get_interview_context(jd_role)
                topic = interview_context["topic"]  # e.g., "product management"
                greeting_role = interview_context["greeting_role"]  # e.g., "Product Manager"
                area_context = interview_context["area_context"]  # e.g., "YouTube Channel Memberships"
                logger.info(f"🎯 JD context: topic='{topic}', role='{greeting_role}', area='{area_context}'")
            else:
                topic = analysis.get("detected_role") or analysis.get("suggested_topics", ["Technical Interview"])[0]
                greeting_role = topic
                area_context = None
                logger.info(f"🎯 Using resume-detected role: {topic}")
            
            # Add company context if available
            if jd_company:
                custom_context["company_name"] = jd_company
                logger.info(f"🏢 Company detected: {jd_company}")
            
            custom_context["topic"] = topic
            custom_context["target_role"] = greeting_role
            custom_context["area_context"] = area_context
            custom_context["resume_skills"] = resume_skills
            custom_context["analysis"] = analysis
            
            # Start interview
            result = self.flow_controller.start_interview(
                topic, 
                candidate_name, 
                custom_context=custom_context
            )
            
            if result['status'] != 'started':
                return {"success": False, "message": result.get("message")}
            
            # Initialize session
            self.current_session = {
                "session_id": result['session_id'],
                "topic": topic,
                "candidate_name": candidate_name,
                "question_count": 1,
                "start_time": time.time(),
                "mode": "practice"
            }
            
            return {
                "success": True,
                "session_id": result['session_id'],
                "greeting": result.get("greeting", "Welcome!"),
                "first_question": result.get("first_question", ""),
                "question_number": 1,
                "total_questions": Config.MAX_QUESTIONS,
                "topic": topic,
                "experience_level": experience_level,
                "detected_skills": resume_skills,  # Use extracted skills from line 273
                "job_title": jd_role or topic,
                "company_name": jd_company
            }
            
        except Exception as e:
            logger.error(f"Practice mode error: {e}", exc_info=True)
            is_production = os.getenv("ENVIRONMENT") == "production"
            safe_message = InputValidator.sanitize_error_message(e, is_production)
            return {"success": False, "message": safe_message}
    
    # ========================================================================
    # ANSWER PROCESSING
    # ========================================================================
    
    def process_answer(
        self,
        answer_text: str,
        transcription_text: str = ""
    ) -> Dict[str, Any]:
        """Process answer (Returns Data Dict)"""
        
        # Check session
        if not self.current_session:
            return {"success": False, "message": "No active session."}
        
        # Use transcription if provided, but validate it first
        if transcription_text:
            is_valid, error_msg = InputValidator.validate_voice_transcript(transcription_text)
            if not is_valid:
                return {
                    "success": False,
                    "message": error_msg or "Invalid transcription.",
                    "current_data": {
                        "answer": answer_text,
                        "elapsed": int(time.time() - self.current_session["start_time"]),
                        "question_number": self.current_session["question_count"]
                    }
                }
            final_answer = transcription_text
        else:
            final_answer = answer_text
        
        # Validate answer text
        is_valid, error_msg = InputValidator.validate_answer_text(final_answer)
        if not is_valid:
            return {
                "success": False,
                "message": error_msg or "Please provide an answer.",
                "current_data": {
                    "answer": final_answer[:100],  # Truncate for display
                    "elapsed": int(time.time() - self.current_session["start_time"]),
                    "question_number": self.current_session["question_count"]
                }
            }
        
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
                
                return {
                    "success": True,
                    "status": "continue",
                    "evaluation": result.get("evaluation", {}),
                    "feedback": result.get("feedback", ""),
                    "next_question": result.get("next_question", ""),
                    "reasoning": result.get("reasoning", {}),
                    "question_number": result.get("question_number", 2),
                    "elapsed": elapsed
                }
            
            # Handle completion
            elif result["status"] == "completed":
                summary = result.get("summary", {})
                self.current_session = None
                
                return {
                    "success": True,
                    "status": "completed",
                    "summary": summary,
                    "elapsed": elapsed
                }
            
            else:
                 return {
                    "success": False, 
                    "message": result.get('message', 'Unexpected error'),
                    "current_data": {"answer": final_answer, "elapsed": elapsed}
                }
                
        except Exception as e:
            logger.error(f"Error processing answer: {e}", exc_info=True)
            is_production = os.getenv("ENVIRONMENT") == "production"
            safe_message = InputValidator.sanitize_error_message(e, is_production)
            return {"success": False, "message": safe_message}
