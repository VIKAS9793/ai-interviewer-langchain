import gradio as gr
from typing import Dict, Any, cast
from src.ui.styles.theme import create_theme, MINIMAL_CSS
from src.ui.components.feedback import create_progress_display
from src.ui.tabs.interview_tab import create_interview_tab
from src.ui.tabs.practice_tab import create_practice_tab
from src.ui.interfaces import InterviewApp
from src.ui.handlers import InterviewHandlers
from src.ai_interviewer.utils.config import Config  # For MAINTENANCE_MODE flag

def create_interface(app: InterviewApp) -> gr.Blocks:
    """
    Create the main Gradio interface.
    
    Args:
        app: The application controller implementing InterviewApp protocol.
        
    Returns:
        gr.Blocks: The constructed Gradio application.
    """
    with gr.Blocks(
        theme=create_theme(),
        css=MINIMAL_CSS,
        title="AI Technical Interviewer"
    ) as interface:
        
        with gr.Column():
            gr.Markdown(
            f"""
            # 🤖 AI Technical Interviewer
            
            **Powered by Gemini + HuggingFace** | Chain-of-Thought Reasoning | Adaptive Questioning
            """
        )
            
            # Maintenance mode warning
            if Config.MAINTENANCE_MODE:
                gr.Markdown(
                    """
                    ## 🔴 SYSTEM OFFLINE
                    
                    **System Offline for Upgrade (v3.3.0)**
                    
                    We are deploying the new Time-Travel Diffusion (TTD) engine and Global Rate Limiting.
                    
                    Access will resume shortly after final verification.
                    """,
                    elem_classes=["maintenance-banner"]
                )
            else:
                gr.Markdown(
                    """
                    > ℹ️ **FREE TIER:** Gemini API limited to **1 interview/day**. After the first interview, the system automatically switches to **HuggingFace** for continued service (unlimited, but may be slower).
                    """
                )
        
        # Tabs container (for hiding during interview)
        with gr.Column(visible=True) as tabs_container:
            with gr.Tabs():
                interview_tab = create_interview_tab()
                practice_tab = create_practice_tab()
        
        # Progress Display
        progress_display = gr.HTML(
            create_progress_display(0, 0),
            label="Progress"
        )
        
        # Main Content Area
        with gr.Row():
            # Question Display
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
                    """
                )
            
            # Answer Input
            with gr.Column(scale=3):
                gr.Markdown("### 💬 Your Answer")
                
                input_mode = gr.Radio(
                    choices=["✏️ Text", "🎤 Voice"],
                    value="✏️ Text",
                    label="Input Mode",
                    info="Choose how you'd like to answer"
                )
                
                # Text Input
                with gr.Column(visible=True) as text_input_container:
                    answer_input = gr.Textbox(
                        label="Type your response",
                        placeholder="Share your thoughts, approach, and reasoning...",
                        lines=15,
                        max_lines=25,
                        show_label=False
                    )
                
                # Voice Input
                with gr.Column(visible=False) as voice_input_container:
                    gr.Markdown(
                        """
                        **🎤 Voice Recording Instructions:**
                        1. Click the microphone button below
                        2. Allow browser microphone access (if prompted)
                        3. Speak your answer clearly
                        4. Click "Stop" when finished
                        5. Review the transcription and submit
                        """
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
        # EVENT HANDLERS (Adapters)
        # ====================================================================
        
        # Toggle Input Mode
        def toggle_input_mode(mode: str):
            if mode == "🎤 Voice":
                return gr.update(visible=False), gr.update(visible=True)
            else:
                return gr.update(visible=True), gr.update(visible=False)
        
        input_mode.change(
            fn=toggle_input_mode,
            inputs=[input_mode],
            outputs=[text_input_container, voice_input_container]
        )
        
        # Transcribe
        transcribe_btn.click(
            fn=app.transcribe_audio,
            inputs=[audio_input],
            outputs=[transcription_output]
        )
        
        # Start Topic Interview Adapter  
        def on_start_interview(topic, name):
            # Check global interview quota (1 interview/day limit)
            from src.ai_interviewer.utils.rate_limiter import get_global_interview_quota
            quota = get_global_interview_quota()
            
            if quota.is_quota_exhausted:
                # Return error message if daily quota exhausted
                return (
                    "⚠️ **Daily Interview Quota Exhausted**\n\n"
                    "The system allows **1 interview per day** to stay within API limits.\n\n"
                    "Please try again tomorrow. The quota resets at midnight UTC.\n\n"
                    f"Current status: {quota.stats['interviews_completed']}/1 interviews completed today.",
                    "",  # progress
                    gr.update(visible=False),  # answer input
                    gr.update(selected=0),  # tab
                    gr.update(interactive=True),  # interview btn
                    gr.update(interactive=True),  # practice btn
                )
            
            response = app.start_topic_interview(topic, name)
            return InterviewHandlers.handle_start_interview(response)
        
        interview_tab.start_btn.click(
            fn=on_start_interview,
            inputs=[interview_tab.topic_dropdown, interview_tab.candidate_name],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                interview_tab.start_btn,
                practice_tab.start_btn
            ]
        )
        
        # Start Practice Interview Adapter
        def on_start_practice(resume, text, url, name):
            response = app.start_practice_interview(resume, text, url, name)
            return InterviewHandlers.handle_practice_start(response)

        practice_tab.start_btn.click(
            fn=on_start_practice,
            inputs=[
                practice_tab.resume_upload, 
                practice_tab.jd_text, 
                practice_tab.jd_url, 
                practice_tab.practice_name
            ],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                interview_tab.start_btn,
                practice_tab.start_btn
            ]
        )
        
        # Submit Answer Adapter
        def on_submit_answer(mode: str, text: str, transcription: str):
            final_text = text
            final_transcription = transcription if mode == "🎤 Voice" else ""
            
            response = app.process_answer(final_text, final_transcription)
            # process_answer returns InterviewResponse (dict)
            response_dict: Dict[str, Any] = response
            return InterviewHandlers.handle_process_answer(response_dict)
        
        submit_btn.click(
            fn=on_submit_answer,
            inputs=[input_mode, answer_input, transcription_output],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                interview_tab.start_btn,
                practice_tab.start_btn
            ]
        )
        
        # Submit on Enter (Text only)
        answer_input.submit(
            fn=lambda text: on_submit_answer("✏️ Text", text, ""),
            inputs=[answer_input],
            outputs=[
                interview_display,
                progress_display,
                answer_input,
                tabs_container,
                interview_tab.start_btn,
                practice_tab.start_btn
            ]
        )
        
        # Clear
        def clear_all_inputs():
            return "", None, ""
        
        clear_btn.click(
            fn=clear_all_inputs,
            outputs=[answer_input, audio_input, transcription_output]
        )
    
    return cast(gr.Blocks, interface)
