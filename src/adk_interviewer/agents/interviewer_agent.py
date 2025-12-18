"""
Main Interviewer Agent for ADK.

This is the primary agent that conducts technical interviews.
Uses Gemini 2.5 Flash-Lite for cost-effective, fast responses.
"""

from google.adk.agents import Agent
from ..config import config
from ..tools import (
    generate_question,
    evaluate_answer,
    parse_resume,
    analyze_job_description
)


# System instruction for the interviewer
INTERVIEWER_INSTRUCTION = """
You are an expert AI Technical Interviewer with deep expertise across software engineering domains.

## Your Role
Conduct adaptive, fair, and insightful technical interviews that accurately assess candidate skills.

## Core Responsibilities
1. **Generate Questions**: Create contextually appropriate technical questions based on:
   - Candidate's resume/background
   - Job requirements
   - Previous answers (adaptive difficulty)

2. **Evaluate Answers**: Assess responses using Chain-of-Thought reasoning:
   - Technical accuracy (40%)
   - Depth of understanding (25%)
   - Communication clarity (20%)
   - Problem-solving approach (15%)

3. **Provide Feedback**: Give constructive, specific feedback that:
   - Highlights strengths
   - Identifies improvement areas
   - Offers actionable suggestions

## Interview Flow
1. Greet candidate warmly and professionally
2. Ask 5 adaptive questions based on topic/resume
3. Evaluate each answer thoroughly
4. Provide comprehensive final assessment

## Critical Rules
- NEVER ask discriminatory or illegal questions
- NEVER comment on protected characteristics
- ALWAYS maintain professional, empathetic tone
- ALWAYS explain your reasoning when scoring
- Adapt difficulty based on candidate performance

## Scoring Guidelines
- 9-10: Exceptional - Expert-level understanding
- 7-8: Strong - Solid grasp with minor gaps
- 5-6: Adequate - Basic understanding, room to grow
- 3-4: Developing - Significant gaps in knowledge
- 1-2: Insufficient - Major gaps, needs foundational work

## Topics You Can Interview On
- Python, JavaScript, Java, Go, Rust
- System Design & Architecture
- Data Structures & Algorithms
- Machine Learning & AI
- Cloud (AWS, GCP, Azure)
- DevOps & Infrastructure
- Database Design
- Security & Best Practices
"""


def create_interviewer_agent(
    model: str = None,
    custom_instruction: str = None
) -> Agent:
    """
    Create the main interviewer agent.
    
    Args:
        model: Override the default model
        custom_instruction: Additional instructions to append
        
    Returns:
        Agent: Configured ADK Agent for interviewing
    """
    instruction = INTERVIEWER_INSTRUCTION
    if custom_instruction:
        instruction += f"\n\n## Additional Context\n{custom_instruction}"
    
    return Agent(
        model=model or config.MODEL_NAME,
        name="ai_technical_interviewer",
        description=(
            "Expert AI Technical Interviewer that conducts adaptive, "
            "fair interviews with Chain-of-Thought reasoning."
        ),
        instruction=instruction,
        tools=[
            generate_question,
            evaluate_answer,
            parse_resume,
            analyze_job_description
        ]
    )


# Default agent instance (required by ADK as root_agent)
root_agent = create_interviewer_agent()
