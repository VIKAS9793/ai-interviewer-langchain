"""
Interview Flow Workflow for ADK.

Orchestrates the complete interview process using
SequentialAgent and LoopAgent for structured execution.
"""

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from ..config import config
from ..agents import create_interviewer_agent, create_critic_agent, create_safety_agent


def create_greeter_agent() -> Agent:
    """Create agent that greets candidates."""
    return Agent(
        model=config.MODEL_NAME,
        name="greeter",
        description="Welcomes candidates and sets interview context",
        instruction="""
        You are a friendly interview greeter.
        
        Your job:
        1. Welcome the candidate warmly
        2. Introduce yourself as an AI interviewer
        3. Explain the interview format (5 questions, adaptive difficulty)
        4. Set expectations (be thorough, think aloud, ask clarifications)
        5. Create a comfortable, professional atmosphere
        
        Keep your greeting concise but warm. End by asking if they're ready.
        """,
        tools=[]
    )


def create_question_asker_agent() -> Agent:
    """Create agent that asks a single question."""
    return Agent(
        model=config.MODEL_NAME,
        name="question_asker",
        description="Asks one technical interview question",
        instruction="""
        You are an interview question asker.
        
        Your job:
        1. Generate an appropriate technical question
        2. Consider the candidate's background and previous answers
        3. Adapt difficulty based on performance
        4. Present the question clearly
        5. Give the candidate time to think
        
        After asking, wait for their response.
        """,
        tools=[]
    )


def create_evaluator_agent() -> Agent:
    """Create agent that evaluates answers."""
    return Agent(
        model=config.MODEL_NAME,
        name="evaluator",
        description="Evaluates candidate answers and provides feedback",
        instruction="""
        You are an answer evaluator.
        
        Your job:
        1. Analyze the candidate's response
        2. Score on a 1-10 scale with justification
        3. Identify strengths in their answer
        4. Note areas for improvement
        5. Provide brief, constructive feedback
        
        Be encouraging but honest. Move to the next question smoothly.
        """,
        tools=[]
    )


def create_reporter_agent() -> Agent:
    """Create agent that generates final report."""
    return Agent(
        model=config.MODEL_NAME,
        name="reporter",
        description="Generates comprehensive interview report",
        instruction="""
        You are an interview reporter.
        
        Your job:
        1. Summarize the entire interview
        2. Calculate overall score (average of all questions)
        3. Highlight top strengths demonstrated
        4. Identify key areas for improvement
        5. Provide hiring recommendation (Strong Yes/Yes/Maybe/No)
        6. Thank the candidate for their time
        
        Format your report professionally with clear sections.
        Be constructive and helpful regardless of performance.
        """,
        tools=[]
    )


def create_question_loop(num_questions: int = 5) -> LoopAgent:
    """
    Create a loop for asking multiple questions.
    
    Args:
        num_questions: Number of questions to ask
        
    Returns:
        LoopAgent: Configured loop for Q&A cycle
    """
    return LoopAgent(
        name="question_loop",
        description=f"Asks {num_questions} interview questions",
        sub_agents=[
            create_question_asker_agent(),
            create_evaluator_agent()
        ],
        max_iterations=num_questions
    )


def create_interview_workflow() -> SequentialAgent:
    """
    Create the complete interview workflow.
    
    The flow is:
    1. Greeter welcomes candidate
    2. Question Loop (ask → evaluate × 5)
    3. Reporter generates final assessment
    
    Returns:
        SequentialAgent: Complete interview orchestration
    """
    return SequentialAgent(
        name="interview_workflow",
        description="Complete technical interview from greeting to final report",
        sub_agents=[
            create_greeter_agent(),
            create_question_loop(config.MAX_QUESTIONS),
            create_reporter_agent()
        ]
    )
