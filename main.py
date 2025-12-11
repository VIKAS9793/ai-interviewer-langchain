"""
AI Technical Interviewer - Production-Grade Gradio UI
Clean Architecture | Responsive Design | Accessibility First
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
# THEME CONFIGURATION - Using Gradio's Native Theme System
# ============================================================================

def create_theme() -> gr.Theme:
    """Create consistent theme using Gradio's native system"""
    return gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
        neutral_hue="slate",
        font=("Inter", "system-ui", "sans-serif"),
        font_mono=("IBM Plex Mono", "monospace")
    ).set(
        # Typography
        body_text_size="*text_lg",
        body_text_weight="400",
        
        # Spacing
        # spacing_xl="40px", (Removed for compatibility)
        # spacing_lg="24px",
        # spacing_md="16px",
        
        # Borders
        # radius_lg="16px", (Removed for compatibility)
        # radius_md="12px",
        # radius_sm="8px",
        
        # Shadows
        # shadow_drop="0 4px 6px -1px rgb(0 0 0 / 0.1)",
        # shadow_drop_lg="0 10px 15px -3px rgb(0 0 0 / 0.1)",
        
        # Button
        # button_primary_background_fill="*primary_500",
        # button_primary_background_fill_hover="*primary_600",
        # button_primary_text_size="*text_lg",
        # button_large_padding="16px 32px",
        
        # Input
        # input_background_fill="*neutral_50",
        # input_border_width="2px",
        # input_padding="12px",
        # input_text_size="*text_md"
    )

# ============================================================================
# MINIMAL CSS - Only for Specific Fixes Not in Theme
# ============================================================================

MINIMAL_CSS = """
/* Theme: Enforce Dark Mode & Brand Colors */
.gradio-container {
    color-scheme: dark;
}

/* Fix: Status badges (Dark Mode Optimized) */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.status-ready { background: rgba(30, 64, 175, 0.4); color: #93c5fd; border: 1px solid #1e40af; }
.status-active { background: rgba(22, 101, 52, 0.4); color: #86efac; border: 1px solid #166534; }
.status-error { background: rgba(153, 27, 27, 0.4); color: #fca5a5; border: 1px solid #991b1b; }

/* Fix: Question card emphasis */
.question-card {
    border-left: 4px solid var(--primary-500);
    padding-left: 24px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 0 8px 8px 0;
}

/* Fix: Progress bar container */
.progress-container {
    background: var(--neutral-100);
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
}

.progress-bar {
    background: linear-gradient(90deg, var(--primary-500), var(--secondary-500));
    height: 100%;
    transition: width 0.3s ease;
}

/* Accessibility: Focus indicators */
*:focus-visible {
    outline: 3px solid var(--primary-500);
    outline-offset: 2px;
}

/* Mobile: Responsive text */
@media (max-width: 768px) {
    .gradio-container {
        font-size: 14px;
    }
}
"""

# ============================================================================
# UI COMPONENT BUILDERS - Reusable, Pure Functions
# ============================================================================

def create_progress_display(question_num: int = 0, elapsed_sec: int = 0) -> str:
    """Generate progress display (pure function)"""
    progress_pct = min((question_num / MAX_QUESTIONS) * 100, 100)
    minutes, seconds = divmod(elapsed_sec, 60)
    
    status_text = "Ready" if question_num == 0 else f"Question {question_num}/{MAX_QUESTIONS}"
    status_class = "status-ready" if question_num == 0 else "status-active"
    
    return f"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 16px; background: var(--neutral-50); border-radius: 12px; margin-bottom: 20px;">
        <div style="flex: 1;">
            <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 8px;">
                {status_text}
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress_pct}%;"></div>
            </div>
        </div>
        <div style="font-family: monospace; font-size: 1.2rem; font-weight: 600; min-width: 80px; text-align: center;">
            ⏱️ {minutes:02d}:{seconds:02d}
        </div>
        <div class="status-badge {status_class}">
            {"🟢" if question_num > 0 else "🟡"} {status_text}
        </div>
    </div>
    """

def format_question_display(
    question: str,
    question_num: int,
    total: int = MAX_QUESTIONS,
    context: Optional[str] = None
) -> str:
    """Format question for display"""
    header = f"## Question {question_num} of {total}"
    
    parts = [header]
    
    if context:
        parts.append(f"**Context:** {context}\n")
    
    parts.append(f"<div class='question-card'>\n\n{question}\n\n</div>")
    
    parts.append("---\n\n💡 **Tip:** Take your time to think through your answer. Quality over speed!")
    
    return "\n\n".join(parts)

def format_feedback_display(
    score: int,
    feedback: str,
    next_question: Optional[str] = None,
    question_num: int = 2,
    reasoning: Optional[Dict] = None
) -> str:
    """Format evaluation feedback"""
    score_emoji = "🌟" if score >= 8 else "✅" if score >= 6 else "💡"
    score_color = "#10b981" if score >= 8 else "#f59e0b" if score >= 6 else "#6366f1"
    
    parts = [
        f"## {score_emoji} Score: {score}/10",
        "",
        f"<div style='padding: 16px; background: {score_color}15; border-left: 4px solid {score_color}; border-radius: 8px;'>",
        "",
        feedback,
        "",
        "</div>"
    ]
    
    if reasoning:
        confidence = reasoning.get('confidence', 0.7)
        approach = reasoning.get('question_approach', 'adaptive').replace('_', ' ').title()
        parts.extend([
            "",
            "---",
            "",
            f"**AI Reasoning:** {approach} approach (Confidence: {confidence:.0%})"
        ])
    
    if next_question:
        parts.extend([
            "",
            "---",
            "",
            format_question_display(next_question, question_num, MAX_QUESTIONS)
        ])
    
    return "\n".join(parts)

def format_final_report(
    summary: Dict[str, Any],
    elapsed_sec: int
) -> str:
    """Format final interview report"""
    minutes, seconds = divmod(elapsed_sec, 60)
    avg_score = summary.get('avg_score', 0)
    
    score_emoji = "🏆" if avg_score >= 8 else "🎯" if avg_score >= 6 else "📈"
    
    parts = [
        f"# {score_emoji} Interview Complete!",
        "",
        f"**Duration:** {minutes}m {seconds}s",
        f"**Questions:** {summary.get('questions_asked', MAX_QUESTIONS)}",
        f"**Average Score:** {avg_score:.1f}/10",
        "",
        "---",
        "",
        "## 💪 Strengths",
        ""
    ]
    
    strengths = summary.get('strengths', ['Good technical communication'])[:3]
    for strength in strengths:
        parts.append(f"- {strength}")
    
    parts.extend(["", "## 🎓 Growth Areas", ""])
    
    improvements = summary.get('areas_for_improvement', ['Continue practicing'])[:3]
    for improvement in improvements:
        parts.append(f"- {improvement}")
    
    parts.extend([
        "",
        "---",
        "",
        "**Ready for another round?** Select a new topic and click Start Interview!"
    ])
    
    return "\n".join(parts)

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
    ) -> Tuple[str, str, str, bool, bool, bool]:
        """Start topic-based interview"""
        
        # Validation
        if not candidate_name or not candidate_name.strip():
            return (
                "⚠️ Please enter your name to begin.",
                create_progress_display(0, 0),
                "",
                False,  # tabs visible
                True,   # start enabled
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
        
        try:
            # Start interview
            result = self.flow_controller.start_interview(
                topic=topic,
                name=candidate_name
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
    ):
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
            
            # Get file path (Gradio 4/5 compatibility)
            file_path = resume_file if isinstance(resume_file, str) else resume_file.name
            
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
    ):
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
            gr.update(interactive=True), # Keep enabled to retry? 
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
                final_report = result.get("final_report", "")
                
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

# ============================================================================
# UI CONSTRUCTION - Clean, Composable Interface
# ============================================================================

def create_interface(app: InterviewApplication) -> gr.Blocks:
    """Create Gradio interface using best practices"""
    
    with gr.Blocks(
        theme=create_theme(),
        css=MINIMAL_CSS,
        title="AI Technical Interviewer",
        fill_height=True
    ) as interface:
        
        # Header
        gr.Markdown(
            """
            # 🤖 AI Technical Interviewer
            
            **Powered by Meta LLaMA 3** | Chain-of-Thought Reasoning | Adaptive Questioning
            """,
            elem_classes=["text-center"]
        )
        
        # Tabs container (for hiding during interview)
        with gr.Column(visible=True) as tabs_container:
            with gr.Tabs() as mode_tabs:
                
                # Tab 1: Topic-Based Interview
                with gr.Tab("📝 Technical Interview"):
                    gr.Markdown("### Quick Start Interview")
                    
                    with gr.Row():
                        candidate_name = gr.Textbox(
                            label="Your Name",
                            placeholder="Enter your full name",
                            scale=2
                        )
                        
                        topic_dropdown = gr.Dropdown(
                            label="Interview Topic",
                            choices=TOPICS,
                            value=TOPICS[0],
                            scale=2
                        )
                        
                        start_btn = gr.Button(
                            "Start Interview",
                            variant="primary",
                            size="lg",
                            scale=1
                        )
                
                # Tab 2: Practice Mode
                with gr.Tab("🎯 Practice Mode"):
                    gr.Markdown("### Resume-Based Practice Interview")
                    
                    with gr.Row():
                        with gr.Column():
                            practice_name = gr.Textbox(
                                label="Your Name",
                                placeholder="Enter your full name"
                            )
                            
                            resume_upload = gr.File(
                                label="Upload Resume",
                                file_types=[".pdf", ".docx"],
                                file_count="single"
                            )
                        
                        with gr.Column():
                            jd_url = gr.Textbox(
                                label="Job Description URL (Optional)",
                                placeholder="https://..."
                            )
                            
                            jd_text = gr.Textbox(
                                label="Or Paste Job Description",
                                placeholder="Paste job description text...",
                                lines=4
                            )
                    
                    start_practice_btn = gr.Button(
                        "Analyze & Start Practice",
                        variant="primary",
                        size="lg"
                    )
        
        # Progress Display
        progress_display = gr.HTML(
            create_progress_display(0, 0),
            label="Progress"
        )
        
        # Main Content Area
        with gr.Row():
            # Question Display (Left)
            with gr.Column(scale=2):
                interview_display = gr.Markdown(
                    """
                    ## Welcome! 👋
                    
                    **Get Started:**
                    1. Enter your name
                    2. Select an interview topic (or upload resume for practice)
                    3. Click "Start Interview"
                    4. Answer thoughtfully and honestly
                    
                    **Tips:**
                    - Take your time to think
                    - Explain your reasoning
                    - Ask clarifying questions when needed
                    """,
                    elem_classes=["question-card"]
                )
            
            # Answer Input (Right)
            with gr.Column(scale=3):
                gr.Markdown("### 💬 Your Answer")
                
                # Input Mode Toggle
                input_mode = gr.Radio(
                    choices=["✍️ Text", "🎤 Voice"],
                    value="✍️ Text",
                    label="Input Mode",
                    info="Choose how you'd like to answer"
                )
                
                # Text Input (Default)
                with gr.Column(visible=True) as text_input_container:
                    answer_input = gr.Textbox(
                        label="Type your response",
                        placeholder="Share your thoughts, approach, and reasoning...",
                        lines=15,
                        max_lines=25,
                        show_label=False
                    )
                
                # Voice Input (Hidden by default)
                with gr.Column(visible=False) as voice_input_container:
                    gr.Markdown(
                        """
                        **🎤 Voice Recording Instructions:**
                        1. Click the microphone button below
                        2. Allow browser microphone access (if prompted)
                        3. Speak your answer clearly
                        4. Click "Stop" when finished
                        5. Review the transcription and submit
                        """,
                        elem_classes=["voice-instructions"]
                    )
                    
                    audio_input = gr.Audio(
                        label="Record Your Answer",
                        sources=["microphone"],
                        type="numpy",
                        show_label=False
                    )
                    
                    transcription_output = gr.Textbox(
                        label="Transcription (Auto-generated)",
                        placeholder="Your speech will be transcribed here...",
                        lines=10,
                        interactive=True,
                        info="You can edit the transcription before submitting"
                    )
                    
                    transcribe_btn = gr.Button(
                        "🔄 Transcribe Audio",
                        variant="secondary",
                        size="lg"
                    )
                
                # Submit Controls
                with gr.Row():
                    submit_btn = gr.Button(
                        "📤 Submit Answer",
                        variant="primary",
                        size="lg",
                        scale=3
                    )
                    
                    clear_btn = gr.Button(
                        "🗑️ Clear",
                        variant="secondary",
                        size="lg",
                        scale=1
                    )
        
        # Footer
        gr.Markdown(
            """
            ---
            
            **AI Technical Interviewer** | Built with LangChain, HuggingFace, Gradio
            
            *Features: Adaptive AI • Semantic Evaluation • Real-time Feedback*
            """,
            elem_classes=["text-center"]
        )
        
        # ====================================================================
        # EVENT HANDLERS
        # ====================================================================
        
        # Toggle between Text and Voice input
        def toggle_input_mode(mode: str):
            """Switch between text and voice input"""
            if mode == "🎤 Voice":
                return (
                    gr.update(visible=False),  # Hide text
                    gr.update(visible=True)    # Show voice
                )
            else:
                return (
                    gr.update(visible=True),   # Show text
                    gr.update(visible=False)   # Hide voice
                )
        
        input_mode.change(
            fn=toggle_input_mode,
            inputs=[input_mode],
            outputs=[text_input_container, voice_input_container]
        )
        
        # Transcribe audio
        transcribe_btn.click(
            fn=app.transcribe_audio,
            inputs=[audio_input],
            outputs=[transcription_output]
        )
        
        # Start Topic Interview
        start_btn.click(
            fn=app.start_topic_interview,
            inputs=[topic_dropdown, candidate_name],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                start_btn,
                start_practice_btn
            ]
        )
        
        # Start Practice Interview
        start_practice_btn.click(
            fn=app.start_practice_interview,
            inputs=[resume_upload, jd_text, jd_url, practice_name],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                start_btn,
                start_practice_btn
            ]
        )
        
        # Submit Answer (handles both text and voice)
        def submit_answer_handler(mode: str, text: str, transcription: str):
            """Determine which input to use based on mode"""
            if mode == "🎤 Voice":
                return app.process_answer("", transcription)
            else:
                return app.process_answer(text, "")
        
        submit_btn.click(
            fn=submit_answer_handler,
            inputs=[input_mode, answer_input, transcription_output],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                start_btn,
                start_practice_btn
            ]
        )
        
        # Submit on Enter (Ctrl+Enter) - Text mode only
        answer_input.submit(
            fn=lambda text: app.process_answer(text, ""),
            inputs=[answer_input],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                start_btn,
                start_practice_btn
            ]
        )
        
        # Clear Answer
        def clear_all_inputs():
            """Clear both text and voice inputs"""
            return "", None, ""
        
        clear_btn.click(
            fn=clear_all_inputs,
            outputs=[answer_input, audio_input, transcription_output]
        )
    
    return interface

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