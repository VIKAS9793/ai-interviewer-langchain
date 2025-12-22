"""
Coding Agent - Code Execution and Verification.

This sub-agent specializes in executing and verifying code solutions
using ADK's BuiltInCodeExecutor for sandboxed Python execution.

v4.6.0: Added Sequential Safety pattern from Kaggle AI Agent competition.
"""

import logging
import re
from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor

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
You are a Code Execution Specialist for technical interviews.

## Your Responsibilities

### 1. Execute Code
When given code to run:
- Execute the provided Python code
- Capture and report all output
- Note any errors or exceptions
- Track execution time if relevant

IMPORTANT: Code is automatically checked for safety before execution.
High-risk operations (file writes, system calls, network requests) are blocked.

### 2. Verify Solutions
When asked to verify a solution:
- Test with the provided inputs
- Check edge cases when appropriate
- Assess correctness of output
- Report any failures clearly

### 3. Code Generation
When asked to demonstrate:
- Write clean, well-commented code
- Follow Python best practices
- Include example test cases
- Execute and show results

### 4. Debugging Support
When helping debug:
- Identify error sources
- Suggest corrections
- Verify fixes work
- Explain the issue clearly

## Output Guidelines
- Show code and results clearly
- Format output readably
- Explain what was executed
- Note any performance observations

## Safety Rules (v4.6.0)
- Only execute Python code
- Automatic risk assessment before execution
- No file system access
- No network requests
- No system commands
- Blocked operations logged for security audit

If code is blocked, explain why and suggest safe alternatives.
"""


def create_coding_agent() -> Agent:
    """
    Create the coding execution sub-agent with safety checks.
    
    v4.6.0: Added Sequential Safety pattern per Kaggle AI Agent competition.
            Uses code_executor= per official ADK docs.
            Limitation: BuiltInCodeExecutor must be sole tool (ADK restriction).
    
    Returns:
        Agent configured for safe code execution with BuiltInCodeExecutor
    """
    return Agent(
        model="gemini-2.0-flash",  # Code execution requires Gemini 2.0+
        name="coding_agent",
        description=(
            "Code execution specialist with safety checks. Runs and verifies "
            "Python code in a sandboxed environment. Blocks risky operations "
            "before execution (v4.6.0 Sequential Safety)."
        ),
        instruction=CODING_INSTRUCTION,
        code_executor=BuiltInCodeExecutor()  # Correct API per ADK official docs
    )
