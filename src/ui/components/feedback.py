from typing import Dict, Any, Optional

MAX_QUESTIONS = 5  # Should ideally be imported from config, but keeping simple for now

def create_progress_display(question_num: int = 0, elapsed_sec: int = 0) -> str:
    """Generate progress display (pure function)"""
    progress_pct = min((question_num / MAX_QUESTIONS) * 100, 100)
    minutes, seconds = divmod(elapsed_sec, 60)
    
    status_text = "Ready" if question_num == 0 else f"Question {question_num}/{MAX_QUESTIONS}"
    status_class = "status-ready" if question_num == 0 else "status-active"
    
    return f"""
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 20px;">
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
    
    parts.extend(["", "## 📈 Growth Areas", ""])
    
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
