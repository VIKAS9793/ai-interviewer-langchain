"""
Coding Agent - Code Analysis and Verification.

This sub-agent specializes in analyzing and verifying code solutions.
Provides code review, logic tracing, and technical feedback.

v4.6.0: Added Sequential Safety pattern from Kaggle AI Agent competition.
        Safety checks handled by safety_agent.
v4.7.0: Added A2UI integration for rich UI responses (experimental).
v4.7.1: Fixed tool hallucination bug - instruction now explicitly states
        NO code execution capability to prevent LLM from calling non-existent tools.
"""


import logging
import re
from google.adk.agents import Agent

# A2UI integration (v4.7)
try:
    from ..a2ui.components import get_a2ui_prompt
    A2UI_ENABLED = True
except ImportError:
    A2UI_ENABLED = False
    def get_a2ui_prompt() -> str:
        return ""

logger = logging.getLogger(__name__)

# Dangerous code patterns that require blocking
RISK_PATTERNS = [
    (r'__import__\s*\(', 'Dynamic import'),
    (r'eval\s*\(', 'Direct eval'),
    (r'exec\s*\(', 'Code execution'),
    (r'compile\s*\(', 'Code compilation'),
    (r'os\.system', 'System command'),
    (r'subprocess\.(run|call|Popen)', 'Subprocess execution'),
    (r'open\s*\(.+,\s*["\']w', 'File write'),
    (r'os\.(remove|unlink|rmdir)', 'File deletion'),
    (r'shutil\.(rmtree|move|copy)', 'File manipulation'),
    (r'urllib|requests|httpx', 'Network request'),
]


def assess_code_risk(code: str) -> tuple[float, list[str]]:
    """Assess risk level of code before execution.
    
    Sequential Safety pattern from Kaggle AI Agent winners.
    Blocks high-risk operations before they run.
    
    Args:
        code: Python code to assess
        
    Returns:
        Tuple of (risk_score 0-1, list of detected risks)
    """
    detected_risks = []
    
    for pattern, description in RISK_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            detected_risks.append(description)
    
    # Calculate risk score (0-1)
    risk_score = min(len(detected_risks) * 0.3, 1.0)
    
    return risk_score, detected_risks


# Coding agent instruction
CODING_INSTRUCTION = """
You are a Code Analysis Specialist for technical interviews.

## CRITICAL: NO CODE EXECUTION
You do NOT have any tools to execute code. Do NOT call any functions.
You can only analyze code by reading and reasoning about it.

## Your Responsibilities

### 1. Analyze Code (PRIMARY)
When given code to review:
- Trace through the logic step by step mentally
- Identify potential issues or bugs
- Explain what the code does
- Assess time/space complexity

### 2. Verify Solutions (MANUAL ONLY)
When asked to verify a solution:
- Trace through with the provided inputs BY HAND
- Walk through each step showing values
- Check edge cases by reasoning
- Explain expected output

### 3. Code Suggestions
When asked to help:
- Write clean, well-commented code
- Follow Python best practices
- Explain the logic clearly
- Show example trace-throughs

### 4. Debugging Support
When helping debug:
- Read and analyze the code
- Identify error sources through reasoning
- Suggest corrections
- Explain the issue clearly

## Output Guidelines
- Show your analysis step by step
- Format output readably using markdown
- Trace through code manually showing variable states
- Note complexity observations (Big O)

## What You CANNOT Do
- Execute code (no tools available)
- Run test cases (trace manually instead)
- Call any functions (you have no tools)
"""



def create_coding_agent() -> Agent:
    """
    Create the coding analysis sub-agent with safety checks.
    
    v4.6.0: Added Sequential Safety pattern per Kaggle AI Agent competition.
    v4.7.0: Added A2UI integration for rich UI responses (experimental).
    
    NOTE: Code execution removed due to ADK sub-agent limitation - 
          "Tool use with function calling is unsupported" when used in sub-agents.
          Safety checks are handled by safety_agent instead.
          Risk assessment function (assess_code_risk) available for future use.
    
    Returns:
        Agent configured for code analysis with optional A2UI responses
    """
    # Build instruction with optional A2UI prompt
    full_instruction = CODING_INSTRUCTION
    if A2UI_ENABLED:
        full_instruction += "\n\n" + get_a2ui_prompt()
    
    return Agent(
        model="gemini-2.5-flash-lite",
        name="coding_agent",
        description=(
            "Code analysis specialist with safety checks and A2UI responses (v4.7). "
            "Reviews and analyzes Python code, traces logic, and identifies issues. "
            "Can provide rich UI components for code display."
        ),
        instruction=full_instruction
    )

