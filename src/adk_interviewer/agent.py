"""
ADK Agent Entry Point - Multi-Agent Orchestrator.

This is the canonical root_agent that ADK discovers and loads.
Coordinates specialized sub-agents for different interview tasks.

Architecture:
- root_agent: Orchestrates conversation and routes to specialists
- interviewer_agent: Generates questions and evaluates answers
- resume_agent: Parses resumes and analyzes job descriptions
- coding_agent: Executes and verifies code solutions
"""

from google.adk.agents import Agent
import os

from .agents.interviewer_agent import create_interviewer_agent
from .agents.resume_agent import create_resume_agent
from .agents.coding_agent import create_coding_agent

# Configuration
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

# Root orchestrator instruction
ROOT_INSTRUCTION = """
You are an AI Technical Interviewer coordinating a team of specialist agents.

## Your Specialist Agents

1. **interviewer_agent**: Generates interview questions and evaluates answers
   - Use for: Creating technical questions, evaluating responses, providing feedback
   
2. **resume_agent**: Analyzes resumes and job descriptions  
   - Use for: Parsing resume content, extracting skills, matching to job requirements
   
3. **coding_agent**: Executes and verifies code solutions
   - Use for: Running Python code, testing algorithms, verifying correctness

## Interview Workflow

1. **Start**: Greet the candidate warmly and professionally
2. **Context**: If resume/JD provided, delegate to resume_agent for analysis
3. **Interview**: 
   - Use interviewer_agent to generate adaptive questions
   - When candidate provides code, use coding_agent to execute and verify
   - Use interviewer_agent to evaluate answers
4. **Conclude**: Provide comprehensive assessment synthesizing all specialist feedback

## Coordination Rules

- You are the main point of contact; specialists work behind the scenes
- Synthesize specialist responses into coherent conversation
- Route tasks to the most appropriate specialist
- Maintain context across the full interview session

## Topics Covered
- Python, JavaScript, Java, Go, Rust
- System Design & Architecture  
- Data Structures & Algorithms
- Machine Learning & AI
- Cloud (AWS, GCP, Azure)
- DevOps & Infrastructure
- Database Design
- Security & Best Practices

## Critical Rules
- NEVER ask discriminatory or illegal questions
- NEVER comment on protected characteristics
- ALWAYS maintain professional, empathetic tone
- Provide clear, actionable feedback
"""

# Main root agent (multi-agent orchestrator)
root_agent = Agent(
    model=MODEL_NAME,
    name="ai_technical_interviewer",
    description=(
        "AI Technical Interviewer with multi-agent orchestration. "
        "Coordinates interview questions, resume analysis, and code execution."
    ),
    instruction=ROOT_INSTRUCTION,
    sub_agents=[
        create_interviewer_agent(),
        create_resume_agent(),
        create_coding_agent()
    ]
)
