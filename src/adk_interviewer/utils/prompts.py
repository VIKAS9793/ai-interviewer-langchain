"""
System Prompts for ADK Interviewer.

Centralized prompt management for consistent agent behavior.
"""

SYSTEM_PROMPTS = {
    "greeting": """
Hello! 👋 Welcome to your technical interview.

I'm an AI interviewer powered by Google's Gemini. I'll be asking you {num_questions} technical questions on {topic}.

**How this works:**
1. I'll ask questions adapted to your experience level
2. Think out loud - I value your reasoning process
3. Feel free to ask clarifying questions
4. Take your time, there's no rush

**Tips for success:**
- Explain your thought process
- Use examples when possible
- It's okay to say "I don't know" and reason through it

Are you ready to begin?
""",

    "question_prefix": """
**Question {question_number} of {total_questions}**

{question}
""",

    "evaluation_template": """
## Evaluation

**Score:** {score}/10

**Strengths:**
{strengths}

**Areas for Improvement:**
{improvements}

**Feedback:** {feedback}

---

{transition}
""",

    "final_report": """
# 📊 Interview Assessment Report

## Overall Performance
**Final Score:** {overall_score}/10
**Recommendation:** {recommendation}

---

## Summary
{summary}

## Strengths Demonstrated
{strengths}

## Growth Opportunities
{improvements}

## Detailed Question Breakdown

{question_breakdown}

---

## Next Steps
{next_steps}

---

Thank you for participating in this interview! 
Your performance shows {performance_summary}.

Best of luck with your career journey! 🚀
""",

    "error_recovery": """
I apologize, but I encountered an issue processing your response.

Let me try a different approach. {recovery_action}

Please feel free to continue, and let me know if you need any clarification.
""",

    "off_topic_redirect": """
I appreciate that, but let's focus on the technical interview.

{redirect}

Now, back to the question...
""",

    "clarification_response": """
Great question! Let me clarify:

{clarification}

Does that help? Feel free to proceed with your answer.
"""
}


def get_greeting(num_questions: int, topic: str) -> str:
    """Generate personalized greeting."""
    return SYSTEM_PROMPTS["greeting"].format(
        num_questions=num_questions,
        topic=topic
    )


def format_question(question: str, question_number: int, total_questions: int) -> str:
    """Format a question for presentation."""
    return SYSTEM_PROMPTS["question_prefix"].format(
        question_number=question_number,
        total_questions=total_questions,
        question=question
    )


def format_evaluation(
    score: float,
    strengths: list,
    improvements: list,
    feedback: str,
    is_last: bool = False
) -> str:
    """Format answer evaluation."""
    transition = "Let's move on to the next question." if not is_last else ""
    
    return SYSTEM_PROMPTS["evaluation_template"].format(
        score=score,
        strengths="\n".join(f"- {s}" for s in strengths),
        improvements="\n".join(f"- {i}" for i in improvements),
        feedback=feedback,
        transition=transition
    )
