import gradio as gr
from dataclasses import dataclass
from src.ui.components.inputs import (
    create_text_input, 
    create_file_upload, 
    create_primary_button
)

@dataclass
class PracticeTabComponents:
    """UI components exposed for event binding"""
    practice_name: gr.Textbox
    resume_upload: gr.File
    jd_url: gr.Textbox
    jd_text: gr.Textbox
    start_btn: gr.Button

def create_practice_tab() -> PracticeTabComponents:
    """
    Create the Practice Mode setup tab.
    
    Returns:
        PracticeTabComponents: Dataclass containing reference to interactive components.
    """
    with gr.TabItem("🎯 Practice Mode"):
        gr.Markdown("### Resume-Based Practice Interview")
        
        gr.Markdown(
            """
            > **📋 What to Expect:** This AI practice tool detects common skills (Python, React, AWS, etc.) and generates adaptive questions based on your resume. Feedback is AI-generated and may vary. For best results, provide detailed answers with examples. Works best with standard resume formats.
            """
        )
        
        with gr.Row():
            with gr.Column():
                practice_name = create_text_input(
                    label="Your Name",
                    placeholder="Enter your full name"
                )
                
                resume_upload = create_file_upload(
                    label="Upload Resume",
                    file_types=[".pdf", ".docx"]
                )
            
            with gr.Column():
                jd_url = create_text_input(
                    label="Job Description URL (Optional)",
                    placeholder="https://..."
                )
                
                # JD Text uses standard Textbox directly for custom lines, 
                # or we could enhance create_text_input. For now, using standard for flexibility if different props needed.
                # Actually, let's use create_text_input but allow lines override if supported.
                # Checking inputs.py: create_text_input has `lines` arg. Perfect.
                jd_text = create_text_input(
                    label="Or Paste Job Description",
                    placeholder="Paste job description text...",
                    lines=4
                )
        
        start_btn = create_primary_button("Analyze & Start Practice")
        
        return PracticeTabComponents(
            practice_name=practice_name,
            resume_upload=resume_upload,
            jd_url=jd_url,
            jd_text=jd_text,
            start_btn=start_btn
        )
