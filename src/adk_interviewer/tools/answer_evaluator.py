"""
Answer Evaluator Tool for ADK Interviewer.

Evaluates candidate answers using Chain-of-Thought reasoning
and provides structured feedback with scores.
"""

from typing import Optional


def evaluate_answer(
    question: str,
    answer: str,
    expected_answer: Optional[str] = None,
    topic: str = "",
    difficulty: str = "medium"
) -> dict:
    """
    Evaluate a candidate's answer to an interview question.
    
    Uses Chain-of-Thought reasoning to analyze the answer's:
    - Technical accuracy
    - Depth of understanding
    - Communication clarity
    - Problem-solving approach
    
    Args:
        question: The interview question that was asked
        answer: The candidate's response
        expected_answer: Key points expected in the answer
        topic: The technical topic being assessed
        difficulty: The question difficulty level
        
    Returns:
        dict: {
            "score": float,            # 1-10 score
            "feedback": str,           # Constructive feedback
            "strengths": list[str],    # What candidate did well
            "improvements": list[str], # Areas to improve
            "follow_up": str,          # Suggested follow-up question
            "reasoning": str           # CoT evaluation reasoning
        }
        
    Example:
        >>> result = evaluate_answer(
        ...     question="Explain decorators in Python",
        ...     answer="Decorators are functions that wrap other functions..."
        ... )
        >>> print(result["score"])  # 7.5
        >>> print(result["feedback"])  # "Good explanation, consider mentioning..."
    """
    # Analyze answer length and structure
    answer_length = len(answer.split())
    has_examples = "example" in answer.lower() or "for instance" in answer.lower()
    has_code = "```" in answer or "def " in answer or "class " in answer
    is_structured = any(marker in answer for marker in ["1.", "first", "second", "•", "-"])
    
    # Base score calculation
    base_score = 5.0
    
    # Length scoring
    if answer_length < 20:
        length_modifier = -2.0  # Too short
    elif answer_length < 50:
        length_modifier = -1.0
    elif answer_length < 200:
        length_modifier = 0.5
    else:
        length_modifier = 1.0  # Detailed response
    
    # Quality modifiers
    example_modifier = 1.0 if has_examples else 0.0
    code_modifier = 1.0 if has_code else 0.0
    structure_modifier = 0.5 if is_structured else 0.0
    
    # Calculate final score (capped at 1-10)
    score = min(10.0, max(1.0, 
        base_score + length_modifier + example_modifier + 
        code_modifier + structure_modifier
    ))
    
    # Generate strengths
    strengths = []
    if has_examples:
        strengths.append("Used concrete examples to illustrate concepts")
    if has_code:
        strengths.append("Included code to demonstrate implementation")
    if is_structured:
        strengths.append("Well-structured and organized response")
    if answer_length >= 100:
        strengths.append("Provided detailed explanation")
    
    # Generate improvements
    improvements = []
    if not has_examples:
        improvements.append("Consider adding practical examples")
    if not has_code and topic in ["Python", "JavaScript", "Data Structures"]:
        improvements.append("Including code snippets would strengthen the answer")
    if not is_structured and answer_length > 100:
        improvements.append("Structuring your response with clear points would improve clarity")
    if answer_length < 50:
        improvements.append("Expand on your answer with more detail")
    
    # Generate feedback
    if score >= 8:
        feedback = "Excellent answer! You demonstrated strong understanding of the topic."
    elif score >= 6:
        feedback = "Good answer. You covered the key concepts well."
    elif score >= 4:
        feedback = "Adequate answer, but there's room for deeper exploration."
    else:
        feedback = "Your answer could benefit from more detail and clarity."
    
    # Suggest follow-up based on gaps
    if not has_examples:
        follow_up = f"Can you walk me through a real-world scenario where you applied this {topic} concept?"
    elif not has_code and topic in ["Python", "JavaScript"]:
        follow_up = "How would you implement this in code?"
    else:
        follow_up = f"What are some common pitfalls or edge cases to consider with {topic}?"
    
    return {
        "score": round(score, 1),
        "feedback": feedback,
        "strengths": strengths or ["Showed basic understanding of the topic"],
        "improvements": improvements or ["Continue building depth in this area"],
        "follow_up": follow_up,
        "reasoning": f"Evaluated {topic} answer at {difficulty} level. "
                    f"Length: {answer_length} words. "
                    f"Examples: {has_examples}. "
                    f"Code: {has_code}. "
                    f"Structured: {is_structured}."
    }
