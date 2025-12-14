import gradio as gr
from typing import Tuple, Dict, Any, List

from src.ai_interviewer.utils.config import Config
from src.ui.components.feedback import (
    create_progress_display,
    format_question_display,
    format_feedback_display,
    format_final_report
)

class InterviewHandlers:
    """
    Handles UI events and transforms Controller data into Gradio updates.
    Acts as the View-Model / Presenter.
    """
    
    @staticmethod
    def handle_start_interview(response: Dict[str, Any]) -> Tuple:
        """
        Handle start interview response.
        Expected Tuple: (welcome_msg, progress, answer_box, tabs_visibility, start_btn_interactive, practice_btn_interactive)
        """
        if not response.get("success"):
            error_msg = response.get("message", "Unknown error")
            return (
                f"❌ **Error:** {error_msg}",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),   # Tabs visible
                gr.update(interactive=True), # Start enabled
                gr.update(interactive=True)  # Practice enabled
            )
        
        # Success path
        greeting = response.get("greeting", "Welcome!")
        first_question = response.get("first_question", "")
        topic = response.get("topic", "Interview")
        
        welcome_msg = f"""
# 👋 {greeting}

**Topic:** {topic}

{format_question_display(first_question, 1, response.get("total_questions", Config.MAX_QUESTIONS))}
"""
        
        progress = create_progress_display(1, 0)
        
        return (
            welcome_msg,
            progress,
            "",  # Clear answer box
            gr.update(visible=False),    # Hide tabs
            gr.update(interactive=False), # Disable start
            gr.update(interactive=False)  # Disable practice
        )

    @staticmethod
    def handle_practice_start(response: Dict[str, Any]) -> Tuple:
        """
        Handle practice mode start.
        Same Output Signature.
        """
        if not response.get("success"):
            return (
                f"❌ **Error:** {response.get('message', 'Unknown error')}",
                create_progress_display(0, 0),
                "",
                gr.update(visible=True),
                gr.update(interactive=True),
                gr.update(interactive=True)
            )
            
        topic = response.get("topic", "Practice")
        experience = response.get("experience_level", "Mid")
        skills = ", ".join(response.get("detected_skills", [])[:5])
        
        welcome_msg = f"""
# 🎯 Practice Session Started

**Target Role:** {topic}  
**Experience Level:** {experience}  
**Detected Skills:** {skills}

---

{response.get("greeting", "Welcome!")}

{format_question_display(response.get("first_question", ""), 1, response.get("total_questions", Config.MAX_QUESTIONS))}

---

> ℹ️ **Note:** This is a simulated interview based on your resume.
"""
        
        progress = create_progress_display(1, 0)
        
        return (
            welcome_msg,
            progress,
            "",
            gr.update(visible=False),
            gr.update(interactive=False),
            gr.update(interactive=False)
        )

    @staticmethod
    def handle_process_answer(response: Dict[str, Any]) -> Tuple:
        """
        Handle answer submission.
        Expected Tuple: (display, progress, answer_box, tabs_visibility, start_btn_interactive, practice_btn_interactive)
        """
        if not response.get("success"):
            # Error or Validation Failure
            current_data = response.get("current_data", {})
            return (
                f"⚠️ {response.get('message', 'Error processing answer')}",
                create_progress_display(current_data.get("question_number", 0), current_data.get("elapsed", 0)),
                current_data.get("answer", ""), # Keep text
                gr.update(visible=False), # Maintain current state (hidden tabs)
                gr.update(interactive=True), # Enable retry
                gr.update(interactive=False)
            )
            
        status = response.get("status")
        elapsed = response.get("elapsed", 0)
        
        if status == "continue":
            evaluation = response.get("evaluation", {})
            question_num = response.get("question_number", 2)
            
            display = format_feedback_display(
                score=evaluation.get("score", 5),
                feedback=response.get("feedback", ""),
                next_question=response.get("next_question", ""),
                question_num=question_num,
                reasoning=response.get("reasoning", {})
            )
            
            progress = create_progress_display(question_num, elapsed)
            
            return (
                display,
                progress,
                "",  # Clear answer box
                gr.update(visible=False),
                gr.update(interactive=True), # Enable for next
                gr.update(interactive=False)
            )
            
        elif status == "completed":
            summary = response.get("summary", {})
            
            display = format_final_report(summary, elapsed)
            progress = create_progress_display(Config.MAX_QUESTIONS, elapsed)
            
            return (
                display,
                progress,
                "",
                gr.update(visible=True),    # Show tabs again
                gr.update(interactive=True), # Enable start
                gr.update(interactive=True)
            )
            
        return (
            "❌ Unexpected status",
            create_progress_display(0, 0),
            "",
            gr.update(visible=True),
            gr.update(interactive=True),
            gr.update(interactive=True)
        )
