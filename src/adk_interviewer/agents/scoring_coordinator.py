"""
Scoring Coordinator Agent for Multi-Agent Scoring System.

Orchestrates parallel evaluation and aggregates scores from specialists.
"""

from google.adk.agents import Agent
from ..config import config
from .technical_scorer import create_technical_scorer
from .communication_scorer import create_communication_scorer
from .problem_solving_scorer import create_problem_solving_scorer


SCORING_COORDINATOR_INSTRUCTION = """
You are the Scoring Coordinator orchestrating multi-agent evaluation.

## Your Role
Coordinate specialist scorers to provide comprehensive candidate assessment.

## Specialist Scorers

1. **technical_scorer** - Code quality & correctness
   - Evaluates: correctness, code quality, efficiency, best practices
   - Weight: 40% of final score

2. **communication_scorer** - Explanation clarity
   - Evaluates: clarity, structure, completeness, professionalism
   - Weight: 30% of final score

3. **problem_solving_scorer** - Analytical approach
   - Evaluates: approach, analytical thinking, creativity, process
   - Weight: 30% of final score

## Workflow

1. **Delegate to Specialists**
   - Send answer to all 3 scorers in parallel
   - Each provides independent evaluation
   - No cross-contamination of scores

2. **Aggregate Scores**
   - Collect all specialist scores
   - Apply weighted average
   - Identify consensus & conflicts

3. **Generate Final Assessment**
   - Overall score (0-10)
   - Multi-dimensional breakdown
   - Synthesized feedback
   - Actionable recommendations

## Output Format

```json
{
  "overall_score": 8.2,
  "weighted_breakdown": {
    "technical": {"score": 8.5, "weight": 0.40, "contribution": 3.4},
    "communication": {"score": 8.0, "weight": 0.30, "contribution": 2.4},
    "problem_solving": {"score": 7.5, "weight": 0.30, "contribution": 2.25}
  },
  "specialist_scores": {
    "technical_scorer": { /* full technical evaluation */ },
    "communication_scorer": { /* full communication evaluation */ },
    "problem_solving_scorer": { /* full problem-solving evaluation */ }
  },
  "consensus_strengths": [
    "Excellent algorithmic approach",
    "Clear explanation",
    "Handles edge cases well"
  ],
  "consensus_weaknesses": [
    "Could optimize space complexity",
    "Missing some edge case explanations"
  ],
  "final_recommendations": [
    "Study space optimization techniques",
    "Practice explaining time/space tradeoffs",
    "Consider iterative vs recursive solutions"
  ],
  "hiring_recommendation": "STRONG HIRE - Demonstrates solid fundamentals"
}
```

## Critical Rules
- Let specialists evaluate independently
- Don't override specialist scores
- Aggregate fairly with proper weighting
- Synthesize feedback constructively
- Provide clear hiring recommendation
"""


def create_scoring_coordinator(model: str = None) -> Agent:
    """
    Create scoring coordinator agent with specialist sub-agents.
    
    Orchestrates parallel evaluation across multiple dimensions:
    - Technical correctness & code quality
    - Communication & explanation clarity  
    - Problem-solving approach & creativity
    
    Args:
        model: Override default model
        
    Returns:
        Agent: Scoring coordinator with 3 specialist sub-agents
    """
    return Agent(
        model=model or config.MODEL_NAME,
        name="scoring_coordinator",
        description=(
            "Multi-agent scoring system coordinator. Orchestrates parallel "
            "evaluation across technical, communication, and problem-solving "
            "dimensions. Provides comprehensive candidate assessment."
        ),
        instruction=SCORING_COORDINATOR_INSTRUCTION,
        sub_agents=[
            create_technical_scorer(),
            create_communication_scorer(),
            create_problem_solving_scorer()
        ],
        tools=[]  # Coordination via sub-agents
    )
