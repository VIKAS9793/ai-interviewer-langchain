import gradio as gr
from dataclasses import dataclass
from src.ai_interviewer.utils.config import Config
from src.ui.components.inputs import (
    create_text_input, 
    create_dropdown, 
    create_primary_button
)

@dataclass
class InterviewTabComponents:
    """UI components exposed for event binding"""
    candidate_name: gr.Textbox
    topic_dropdown: gr.Dropdown
    start_btn: gr.Button

def create_interview_tab() -> InterviewTabComponents:
    """
    Create the Technical Interview setup tab.
    
    Returns:
        InterviewTabComponents: Dataclass containing reference to interactive components.
    """
    with gr.TabItem("📝 Technical Interview"):
        gr.Markdown("### Quick Start Interview")
        
        with gr.Row():
            candidate_name = create_text_input(
                label="Your Name",
                placeholder="Enter your full name"
            )
            
            topic_dropdown = create_dropdown(
                label="Interview Topic",
                choices=Config.AVAILABLE_TOPICS,
                value=Config.AVAILABLE_TOPICS[0] if Config.AVAILABLE_TOPICS else None
            )
            
        start_btn = create_primary_button("Start Interview")
        
        return InterviewTabComponents(
            candidate_name=candidate_name,
            topic_dropdown=topic_dropdown,
            start_btn=start_btn
        )
