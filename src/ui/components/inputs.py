import gradio as gr
from typing import List, Optional, Literal, cast

def create_text_input(
    label: str,
    placeholder: str = "",
    lines: int = 1,
    visible: bool = True
) -> gr.Textbox:
    """Create a standardized text input with proper padding"""
    # Using elem_id for maximum CSS specificity
    import uuid
    unique_id = f"input-{uuid.uuid4().hex[:8]}"
    return gr.Textbox(
        label=label,
        placeholder=f"   {placeholder}",  # Workaround: add spaces to placeholder
        lines=lines,
        visible=visible,
        elem_classes=["input-standard"],
        elem_id=unique_id,
        container=True,  # Keep container for label
        scale=1
    )

def create_dropdown(
    label: str,
    choices: List[str],
    value: Optional[str] = None,
    visible: bool = True
) -> gr.Dropdown:
    """Create a standardized dropdown"""
    return gr.Dropdown(
        label=label,
        choices=choices,
        value=value or choices[0] if choices else None,
        visible=visible,
        elem_classes=["dropdown-standard"],
        interactive=True
    )

def create_file_upload(
    label: str,
    file_types: List[str] = [".pdf", ".docx"],
    visible: bool = True
) -> gr.File:
    """Create a standardized file upload"""
    return gr.File(
        label=label,
        file_types=file_types,
        visible=visible,
        elem_classes=["dark-file-upload"], # Uses our custom CSS
        height=100
    )

def create_primary_button(
    text: str,
    variant: str = "primary",  # primary or secondary
    size: str = "lg"
) -> gr.Button:
    """Create a CTA button"""
    # Cast to Literal types expected by Gradio
    variant_literal = cast(Literal["primary", "secondary", "stop", "huggingface"], variant)
    size_literal = cast(Literal["sm", "md", "lg"], size)
    return gr.Button(
        value=text,
        variant=variant_literal,
        size=size_literal,
        elem_classes=["pill-btn"] if variant == "primary" else []
    )
