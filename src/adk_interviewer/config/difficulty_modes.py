"""
Interview Difficulty Modes Configuration.

Defines Quick/Standard/Deep interview tracks following NotebookLM pattern.
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class DifficultyMode(str, Enum):
    """Interview difficulty modes."""
    QUICK_SCREEN = "quick_screen"
    STANDARD = "standard"
    DEEP_TECHNICAL = "deep_technical"


@dataclass
class ModeConfig:
    """Configuration for an interview difficulty mode."""
    
    # Mode metadata
    name: str
    display_name: str
    description: str
    
    # Time constraints
    duration_minutes: int
    
    # Question parameters
    min_questions: int
    max_questions: int
    difficulty_distribution: Dict[str, float]  # easy, medium, hard, expert percentages
    
    # Evaluation depth
    evaluation_depth: str  # surface, standard, comprehensive
    use_multi_agent_scoring: bool
    
    # Feedback detail
    feedback_level: str  # minimal, standard, detailed


# Mode configurations
DIFFICULTY_MODES: Dict[DifficultyMode, ModeConfig] = {
    DifficultyMode.QUICK_SCREEN: ModeConfig(
        name="quick_screen",
        display_name="Quick Screen",
        description="Fast initial screening (15 min). Basic concepts only.",
        duration_minutes=15,
        min_questions=3,
        max_questions=5,
        difficulty_distribution={
            "easy": 0.7,      # 70% easy
            "medium": 0.3,    # 30% medium
            "hard": 0.0,      # 0% hard
            "expert": 0.0     # 0% expert
        },
        evaluation_depth="surface",
        use_multi_agent_scoring=False,
        feedback_level="minimal"
    ),
    
    DifficultyMode.STANDARD: ModeConfig(
        name="standard",
        display_name="Standard Interview",
        description="Comprehensive technical interview (45 min). Balanced difficulty.",
        duration_minutes=45,
        min_questions=8,
        max_questions=12,
        difficulty_distribution={
            "easy": 0.25,     # 25% easy
            "medium": 0.50,   # 50% medium
            "hard": 0.25,     # 25% hard
            "expert": 0.0     # 0% expert
        },
        evaluation_depth="standard",
        use_multi_agent_scoring=True,
        feedback_level="standard"
    ),
    
    DifficultyMode.DEEP_TECHNICAL: ModeConfig(
        name="deep_technical",
        display_name="Deep Technical Interview",
        description="In-depth senior/expert interview (90 min). Advanced concepts.",
        duration_minutes=90,
        min_questions=15,
        max_questions=20,
        difficulty_distribution={
            "easy": 0.1,      # 10% easy (warmup)
            "medium": 0.3,    # 30% medium
            "hard": 0.4,      # 40% hard
            "expert": 0.2     # 20% expert
        },
        evaluation_depth="comprehensive",
        use_multi_agent_scoring=True,
        feedback_level="detailed"
    )
}


def get_mode_config(mode: DifficultyMode) -> ModeConfig:
    """
    Get configuration for a difficulty mode.
    
    Args:
        mode: The difficulty mode enum
        
    Returns:
        ModeConfig: Configuration for the mode
    """
    return DIFFICULTY_MODES[mode]


def get_difficulty_for_question_number(mode: DifficultyMode, question_num: int) -> str:
    """
    Determine difficulty level for a specific question number.
    
    Uses the mode's difficulty distribution to select appropriate difficulty.
    
    Args:
        mode: Current interview difficulty mode
        question_num: Question number in sequence (1-indexed)
        
    Returns:
        str: Difficulty level ("easy", "medium", "hard", "expert")
    """
    config = get_mode_config(mode)
    dist = config.difficulty_distribution
    
    # Simple weighted selection based on distribution
    # For better UX, start easier and ramp up
    total_questions = config.max_questions
    progress = question_num / total_questions
    
    if progress < 0.3:  # First 30% - easier
        if dist["easy"] > 0:
            return "easy"
        elif dist["medium"] > 0:
            return "medium"
    elif progress < 0.7:  # Middle 40% - normal distribution
        if dist["medium"] > 0.3:
            return "medium"
        elif dist["hard"] > 0:
            return "hard"
    else:  # Last 30% - harder
        if dist["hard"] > 0:
            return "hard"
        elif dist["expert"] > 0:
            return "expert"
        elif dist["medium"] > 0:
            return "medium"
    
    # Fallback to most common difficulty
    return max(dist.items(), key=lambda x: x[1])[0]


def format_mode_description(mode: DifficultyMode) -> str:
    """
    Format user-friendly description of interview mode.
    
    Args:
        mode: Difficulty mode
        
    Returns:
        str: Formatted description
    """
    config = get_mode_config(mode)
    
    return f"""
**{config.display_name}**

{config.description}

- **Duration:** {config.duration_minutes} minutes
- **Questions:** {config.min_questions}-{config.max_questions}
- **Evaluation:** {config.evaluation_depth.title()}
- **Scoring:** {"Multi-Agent" if config.use_multi_agent_scoring else "Single Agent"}
"""
