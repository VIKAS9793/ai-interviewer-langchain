import gradio as gr

def create_theme() -> gr.Theme:
    """Create dark theme with high contrast for accessibility"""
    return gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="purple",
        neutral_hue="slate",
        font=["Inter", "system-ui", "sans-serif"],
        font_mono=["IBM Plex Mono", "monospace"]
    ).set(
        # Dark Backgrounds
        body_background_fill="#0f172a",
        body_background_fill_dark="#0f172a",
        block_background_fill="#1e293b",
        block_background_fill_dark="#1e293b",
        
        # High Contrast Text
        body_text_color="#f1f5f9",
        body_text_color_dark="#f1f5f9",
        block_label_text_color="#e2e8f0",
        block_label_text_color_dark="#e2e8f0",
        block_title_text_color="#f8fafc",
        block_title_text_color_dark="#f8fafc",
        
        # Borders
        border_color_primary="#475569",
        border_color_primary_dark="#475569",
        
        # Buttons
        button_primary_background_fill="#6366f1",
        button_primary_background_fill_hover="#818cf8",
        button_primary_text_color="#ffffff",
        button_secondary_background_fill="#334155",
        button_secondary_background_fill_hover="#475569",
        button_secondary_text_color="#e2e8f0",
        
        # Inputs
        input_background_fill="#1e293b",
        input_background_fill_dark="#1e293b",
        input_border_color="#475569",
        input_border_color_dark="#475569",
        input_placeholder_color="#94a3b8",
    )

# ============================================================================
# CSS CONFIGURATION
# ============================================================================

MINIMAL_CSS = """
/* Dark Mode Foundation */
.gradio-container {
    color-scheme: dark;
    background: #0f172a !important;
    max-width: 1200px !important; /* Prevent excessive width on large screens */
    margin: 0 auto !important;
    padding: 20px !important; /* FIX: Added global padding to prevent edge sticking */
}

/* Fix: Text stuck to borders in Markdown */
.prose p, .prose li {
    margin-bottom: 0.5em !important;
    line-height: 1.6 !important;
}

/* High Contrast Text - Force visibility on ALL elements */
.gradio-container, 
.gradio-container *,
.gr-prose, .gr-prose *,
.gr-markdown, .gr-markdown *,
.gr-box, .gr-box *,
.gr-form, .gr-form *,
.gr-panel, .gr-panel *,
.gr-block-label, .gr-block-label *,
.gr-input-label, .gr-input-label *,
[class*="svelte-"], [class*="svelte-"] *,
label, label span,
span, p, div, 
h1, h2, h3, h4, h5, h6,
.label-wrap, .label-wrap *,
.wrap, .wrap *,
input, textarea,
.secondary-wrap, .secondary-wrap *,
.prose, .prose * {
    color: #f1f5f9 !important;
}

/* Ensure input text is visible */
input, textarea, select, option {
    color: #f1f5f9 !important;
    background-color: #1e293b !important;
}

/* Tab labels */
.tab-nav button, .tabs button, [role="tab"] {
    color: #e2e8f0 !important;
}

.tab-nav button.selected, .tabs button.selected, [role="tab"][aria-selected="true"] {
    color: #ffffff !important;
    background: #6366f1 !important;
}

/* Pill-Shaped CTA Buttons */
.pill-btn, .pill-btn button {
    border-radius: 9999px !important;
    padding: 12px 32px !important;
    min-width: auto !important;
    width: fit-content !important;
    max-width: 280px !important;
    margin: 0 auto !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    justify-content: center !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: #ffffff !important;
}

.pill-btn:hover, .pill-btn button:hover {
    background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
}

/* Override Gradio's default full-width button behavior */
.block.svelte-1f354aw, .form.svelte-1f354aw {
    width: fit-content !important;
    margin: 0 auto !important;
}

/* Status Badges */
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

/* Question Card */
.question-card {
    border-left: 4px solid #6366f1;
    padding-left: 24px !important; /* Increase padding */
    padding-right: 24px !important;
    padding-top: 16px !important;
    padding-bottom: 16px !important;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 0 8px 8px 0;
    margin-bottom: 20px !important;
}

/* Progress Bar */
.progress-container {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
}

.progress-bar {
    background: linear-gradient(90deg, #6366f1, #a855f7);
    height: 100%;
    transition: width 0.3s ease;
}

/* Input Fields - High Contrast (Gradio 4.44 compatible) */
textarea, 
input[type="text"], 
input:not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]),
.gr-textbox textarea, 
.gr-textbox input,
[data-testid*="textbox"] input,
[data-testid*="textbox"] textarea {
    background: #1e293b !important;
    border: 1px solid #475569 !important;
    color: #f1f5f9 !important;
    padding: 16px !important; /* Increased padding for text spacing */
    box-sizing: border-box !important;
    border-radius: 8px !important;
    margin: 4px 0 !important;
}

textarea::placeholder, input::placeholder {
    color: #94a3b8 !important;
    padding-left: 4px !important;
}

/* Labels */
label, .gr-form label {
    color: #e2e8f0 !important;
    font-weight: 600;
}

/* Custom Input Standard Class - Following Gradio Official Docs */
/* Pattern from: https://www.gradio.app/guides/custom-CSS-and-JS */
.input-standard textarea,
.input-standard input {
    background: #1e293b !important;
    border: 2px solid #6366f1 !important;
    color: #f1f5f9 !important;
    padding: 16px !important;
    box-sizing: border-box !important;
    border-radius: 8px !important;
    font-size: 16px !important;
}

/* File Upload Component - Force dark theme on ALL nested elements */
.dark-file-upload,
.dark-file-upload *,
.dark-file-upload > div,
.dark-file-upload > div > div,
.dark-file-upload [class*="wrap"],
.dark-file-upload [class*="container"],
.dark-file-upload [class*="drop"],
.dark-file-upload [class*="svelte"] {
    background: #1e293b !important;
    background-color: #1e293b !important;
}

.dark-file-upload {
    border: 2px dashed #6366f1 !important;
    border-radius: 12px !important;
}

/* All text inside - light on dark */
.dark-file-upload span,
.dark-file-upload p,
.dark-file-upload a,
.dark-file-upload div {
    color: #93c5fd !important;
}

/* Upload button specifically */
.dark-file-upload button {
    color: #ffffff !important;
    background: #6366f1 !important;
    background-color: #6366f1 !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
}

/* Accessibility: Focus indicators */
*:focus-visible {
    outline: 3px solid #6366f1;
    outline-offset: 2px;
}

/* Dropdown & Select Menu Fixes */
ul.options, .options, .wrap, .selector, .dropdown-options, 
[class*="options"], [class*="menu"] {
    background: #1e293b !important;
    background-color: #1e293b !important;
    border-color: #475569 !important;
}

li.item, .item, .option, button.item {
    color: #f1f5f9 !important;
    background: #1e293b !important;
}

li.item:hover, .item:hover, .option:hover,
li.item.selected, .item.selected,
.selected.item {
    background: #334155 !important;
    color: #ffffff !important;
}

/* Fix for SVG icons in dropdowns */
.selector svg, .wrap svg, .options svg {
    fill: #f1f5f9 !important;
    stroke: #f1f5f9 !important;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .gradio-container {
        font-size: 14px;
        padding: 10px !important; /* Smaller padding on mobile */
    }
    button.primary, button.secondary {
        padding: 6px 16px !important;
    }
}
"""
