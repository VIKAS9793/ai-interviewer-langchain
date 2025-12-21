"""
Hint Provider Tool for Study Mode.

Provides progressive hints for problem-solving without giving direct answers.
Follows Socratic method - guides candidate to solution.
"""


def provide_hints(
    question: str,
    current_approach: str,
    hint_level: int,
    tool_context) -> str:
    """
    Provide progressive hints for interview questions.
    
    NEVER gives direct solution - helps candidate arrive at answer themselves.
    
    Args:
        question: The interview question being solved
        current_approach: Candidate's current thinking/attempt
        hint_level: 1 (gentle), 2 (medium), 3 (detailed)
        tool_context: ADK tool execution context
        
    Returns:
        Hint appropriate for the level - never the full solution
    """
    # This tool uses the LLM to generate adaptive hints
    # The instruction will be passed via the agent's system prompt
    
    # Build hint prompt based on level
    if hint_level == 1:
        # Gentle - high-level direction only
        hint_prompt = f"""
Question: {question}

Candidate's approach: {current_approach}

Provide a GENTLE HINT (Level 1):
- Point to the right direction or pattern
- Ask guiding questions
- NO code, NO specific algorithms
- Just help them think about the problem differently

Example: "Have you considered what data structure would give O(1) lookup?"
"""
    
    elif hint_level == 2:
        # Medium - algorithm/approach suggestion
        hint_prompt = f"""
Question: {question}

Candidate's approach: {current_approach}

Provide a MEDIUM HINT (Level 2):
- Suggest the algorithm or approach
- Outline the high-level steps
- Still NO code implementation
- Help them understand the strategy

Example: "Try using a hash map to track seen elements. What would you store as key and value?"
"""
    
    else:  # hint_level == 3
        # Detailed - pseudocode, but not full solution
        hint_prompt = f"""
Question: {question}

Candidate's approach: {current_approach}

Provide a DETAILED HINT (Level 3):
- Give pseudocode or detailed algorithm steps
- Show the pattern clearly
- Still avoid writing the complete solution
- Let them implement the final details

Example:
```
1. Initialize hash map
2. For each element:
   a. Check if element exists in map
   b. If yes, return the pair
   c. If no, store complement in map
3. Return None if no pair found
```
"""
    
    # Return the hint prompt
    # The LLM (via study_agent) will generate the actual hint
    return hint_prompt


# Hint generation guidelines (embedded in study_agent instruction)
HINT_GUIDELINES = """
## Hint Generation Principles (Socratic Method)

**Level 1 - Gentle:**
- Ask guiding questions
- Point to relevant concepts
- No specific algorithms or code
- Example: "What's the time complexity of your current approach? Can we do better?"

**Level 2 - Medium:**
- Suggest algorithm/data structure
- Outline approach at high level
- Still no implementation details
- Example: "Use two pointers - one at start, one at end. How would they move?"

**Level 3 - Detailed:**
- Provide pseudocode
- Show clear algorithm steps
- Stop before complete implementation
- Example: Pseudocode with step-by-step logic, but candidate fills in details

**NEVER:**
- Give complete, working solution
- Write full implementation
- Solve the problem for the candidate
- Answer directly without guiding thought process

**ALWAYS:**
- Help candidate learn and understand
- Build problem-solving skills
- Encourage thinking and exploration
- Celebrate progress and attempts
"""
