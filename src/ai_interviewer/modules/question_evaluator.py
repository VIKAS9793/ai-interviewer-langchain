"""
Question Quality Evaluator Module

Part of TTD (Test-Time Diffusion) Algorithm Implementation.
Provides programmatic quality scoring (0-10) for interview questions.

Architecture:
    Supervisor → Parallel Generators → Red Team → [Evaluator] → Refinement

Reference:
    TTD-DR (Test-Time Diffusion Deep Researcher) architecture
    Source: levelup.gitconnected.com (building-a-human-level-deep-research-agentic-system)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Dimensions for evaluating question quality."""
    RELEVANCE = "relevance"  # To interview topic
    CLARITY = "clarity"  # Understandability
    DIFFICULTY = "difficulty"  # Appropriate level
    UNIQUENESS = "uniqueness"  # Not repetitive
    DEPTH = "depth"  # Technical depth
    ACTIONABILITY = "actionability"  # Can be answered


@dataclass
class QuestionQualityScore:
    """
    Quality assessment result for a question.
    
    Each dimension is scored 0-10. Overall is weighted average.
    """
    overall: float = 0.0  # Weighted average of all dimensions
    relevance: float = 0.0  # How relevant to the topic
    clarity: float = 0.0  # How clear and understandable
    difficulty: float = 0.0  # Appropriate difficulty level
    uniqueness: float = 0.0  # Not similar to previous questions
    depth: float = 0.0  # Technical depth
    actionability: float = 0.0  # Can the candidate answer this?
    
    critique: str = ""  # Summary of issues
    suggestions: List[str] = field(default_factory=list)  # Improvement suggestions
    passed: bool = False  # Met minimum quality threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "overall": self.overall,
            "dimensions": {
                "relevance": self.relevance,
                "clarity": self.clarity,
                "difficulty": self.difficulty,
                "uniqueness": self.uniqueness,
                "depth": self.depth,
                "actionability": self.actionability
            },
            "critique": self.critique,
            "suggestions": self.suggestions,
            "passed": self.passed
        }


class QuestionEvaluator:
    """
    Programmatic evaluator for question quality.
    
    Implements TTD's quality scoring component:
    - Scores quality on multiple dimensions (0-10)
    - Triggers refinement if score drops below threshold
    - Tracks improvement over iterations
    
    Can use either:
    - Heuristic evaluation (fast, no LLM call)
    - LLM-based evaluation (more accurate, uses API call)
    """
    
    # Weights for calculating overall score
    DIMENSION_WEIGHTS = {
        QualityDimension.RELEVANCE: 0.25,
        QualityDimension.CLARITY: 0.20,
        QualityDimension.DIFFICULTY: 0.15,
        QualityDimension.UNIQUENESS: 0.20,
        QualityDimension.DEPTH: 0.10,
        QualityDimension.ACTIONABILITY: 0.10,
    }
    
    # Minimum threshold for question acceptance
    MIN_QUALITY_THRESHOLD = 7.0
    
    def __init__(self, use_llm: bool = False, llm=None):
        """
        Initialize evaluator.
        
        Args:
            use_llm: If True, use LLM for evaluation (more accurate but slower)
            llm: LLM instance for LLM-based evaluation
        """
        self.use_llm = use_llm
        self.llm = llm
        self.evaluation_history: List[QuestionQualityScore] = []
        
        logger.info(f"📊 QuestionEvaluator initialized (use_llm={use_llm})")
    
    def evaluate(
        self, 
        question: str, 
        topic: str,
        previous_questions: Optional[List[str]] = None,
        target_difficulty: str = "medium"
    ) -> QuestionQualityScore:
        """
        Evaluate question quality across multiple dimensions.
        
        Args:
            question: The question to evaluate
            topic: Interview topic for relevance check
            previous_questions: List of previously asked questions
            target_difficulty: Expected difficulty level
            
        Returns:
            QuestionQualityScore with scores and recommendations
        """
        if self.use_llm and self.llm is not None:
            return self._evaluate_with_llm(question, topic, previous_questions, target_difficulty)
        else:
            return self._evaluate_heuristic(question, topic, previous_questions, target_difficulty)
    
    def _evaluate_heuristic(
        self, 
        question: str, 
        topic: str,
        previous_questions: Optional[List[str]] = None,
        target_difficulty: str = "medium"
    ) -> QuestionQualityScore:
        """
        Fast heuristic evaluation without LLM call.
        
        Uses rule-based scoring for quick assessment.
        """
        previous_questions = previous_questions or []
        question_lower = question.lower()
        topic_lower = topic.lower()
        
        issues = []
        suggestions = []
        
        # === RELEVANCE (0-10) ===
        topic_words = set(topic_lower.split())
        question_words = set(question_lower.split())
        common_words = topic_words & question_words
        
        relevance = min(10, len(common_words) * 3 + 4)  # Base 4, +3 per match
        if relevance < 5:
            issues.append("Question may not be relevant to topic")
            suggestions.append(f"Include keywords related to {topic}")
        
        # === CLARITY (0-10) ===
        # Good questions are 10-50 words, have proper structure
        word_count = len(question.split())
        if 10 <= word_count <= 50:
            clarity = 9
        elif 5 <= word_count < 10 or 50 < word_count <= 70:
            clarity = 7
        else:
            clarity = 5
            issues.append("Question length is suboptimal")
            suggestions.append("Aim for 10-50 words for clarity")
        
        # Check for question mark
        if "?" in question:
            clarity = min(10, clarity + 1)
        else:
            issues.append("Missing question mark")
            suggestions.append("Add a question mark for clarity")
        
        # === DIFFICULTY (0-10) ===
        difficulty_keywords = {
            "easy": ["what is", "define", "list", "name", "describe"],
            "medium": ["how", "explain", "compare", "when would", "why"],
            "hard": ["design", "optimize", "trade-off", "scale", "debug", "architect"]
        }
        
        detected_difficulty = "medium"
        for level, keywords in difficulty_keywords.items():
            if any(kw in question_lower for kw in keywords):
                detected_difficulty = level
                break
        
        if detected_difficulty == target_difficulty:
            difficulty = 10
        elif (detected_difficulty == "easy" and target_difficulty == "medium") or \
             (detected_difficulty == "medium" and target_difficulty == "hard"):
            difficulty = 7
        else:
            difficulty = 5
            issues.append(f"Difficulty mismatch: expected {target_difficulty}, got {detected_difficulty}")
        
        # === UNIQUENESS (0-10) ===
        # Check using semantic deduplication
        try:
            from src.ai_interviewer.modules.semantic_dedup import is_semantic_duplicate
            if previous_questions and is_semantic_duplicate(question, previous_questions):
                uniqueness = 2
                issues.append("Question is semantically similar to a previous question")
                suggestions.append("Generate a question on a different aspect")
            else:
                uniqueness = 10
        except Exception as e:
            logger.warning(f"Semantic check failed: {e}")
            # Fallback to simple check
            if any(question.lower() in prev.lower() or prev.lower() in question.lower() 
                   for prev in previous_questions):
                uniqueness = 3
            else:
                uniqueness = 8
        
        # === DEPTH (0-10) ===
        depth_indicators = ["specific", "example", "case", "scenario", "production", 
                           "real-world", "experience", "implementation", "design"]
        depth_count = sum(1 for indicator in depth_indicators if indicator in question_lower)
        depth = min(10, 5 + depth_count)
        
        # === ACTIONABILITY (0-10) ===
        # Can the candidate actually answer this?
        if "you" in question_lower or "your" in question_lower:
            actionability = 9  # Personal experience questions are actionable
        elif any(w in question_lower for w in ["explain", "describe", "how", "what"]):
            actionability = 8  # Knowledge questions are actionable
        else:
            actionability = 6
        
        # Calculate overall score (weighted average)
        overall = (
            relevance * self.DIMENSION_WEIGHTS[QualityDimension.RELEVANCE] +
            clarity * self.DIMENSION_WEIGHTS[QualityDimension.CLARITY] +
            difficulty * self.DIMENSION_WEIGHTS[QualityDimension.DIFFICULTY] +
            uniqueness * self.DIMENSION_WEIGHTS[QualityDimension.UNIQUENESS] +
            depth * self.DIMENSION_WEIGHTS[QualityDimension.DEPTH] +
            actionability * self.DIMENSION_WEIGHTS[QualityDimension.ACTIONABILITY]
        )
        
        # Create result
        result = QuestionQualityScore(
            overall=round(overall, 2),
            relevance=relevance,
            clarity=clarity,
            difficulty=difficulty,
            uniqueness=uniqueness,
            depth=depth,
            actionability=actionability,
            critique="; ".join(issues) if issues else "Question meets quality standards",
            suggestions=suggestions,
            passed=overall >= self.MIN_QUALITY_THRESHOLD
        )
        
        self.evaluation_history.append(result)
        
        log_level = logging.INFO if result.passed else logging.WARNING
        logger.log(log_level, 
            f"📊 Question evaluated: {overall:.1f}/10 ({'✅ PASSED' if result.passed else '❌ FAILED'})"
        )
        
        return result
    
    def _evaluate_with_llm(
        self, 
        question: str, 
        topic: str,
        previous_questions: Optional[List[str]] = None,
        target_difficulty: str = "medium"
    ) -> QuestionQualityScore:
        """
        LLM-based evaluation for more accurate scoring.
        
        Uses the LLM to assess question quality across dimensions.
        """
        if not self.llm:
            logger.warning("LLM not available, falling back to heuristic")
            return self._evaluate_heuristic(question, topic, previous_questions, target_difficulty)
        
        previous_str = "\n".join(f"- {q}" for q in (previous_questions or [])) or "None"
        
        prompt = f"""[INST] You are a question quality evaluator for technical interviews.
        
Evaluate this interview question on a scale of 0-10 for each dimension:

QUESTION: {question}
TOPIC: {topic}
TARGET DIFFICULTY: {target_difficulty}
PREVIOUS QUESTIONS:
{previous_str}

Respond in this exact format (numbers only for scores):
RELEVANCE: [0-10]
CLARITY: [0-10]
DIFFICULTY: [0-10]
UNIQUENESS: [0-10]
DEPTH: [0-10]
ACTIONABILITY: [0-10]
CRITIQUE: [one sentence summary of issues, or "None"]
SUGGESTION: [one improvement suggestion, or "None"]
[/INST]"""

        try:
            response_obj = self.llm.invoke(prompt)
            response = (response_obj.content if hasattr(response_obj, 'content') else str(response_obj))
            
            # Parse response
            scores = {}
            critique = ""
            suggestion = ""
            
            for line in response.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key in ["RELEVANCE", "CLARITY", "DIFFICULTY", "UNIQUENESS", "DEPTH", "ACTIONABILITY"]:
                        try:
                            scores[key.lower()] = float(value.split()[0])
                        except (ValueError, IndexError):
                            scores[key.lower()] = 5.0
                    elif key == "CRITIQUE":
                        critique = value
                    elif key == "SUGGESTION":
                        suggestion = value
            
            # Calculate overall
            overall = (
                scores.get("relevance", 5) * self.DIMENSION_WEIGHTS[QualityDimension.RELEVANCE] +
                scores.get("clarity", 5) * self.DIMENSION_WEIGHTS[QualityDimension.CLARITY] +
                scores.get("difficulty", 5) * self.DIMENSION_WEIGHTS[QualityDimension.DIFFICULTY] +
                scores.get("uniqueness", 5) * self.DIMENSION_WEIGHTS[QualityDimension.UNIQUENESS] +
                scores.get("depth", 5) * self.DIMENSION_WEIGHTS[QualityDimension.DEPTH] +
                scores.get("actionability", 5) * self.DIMENSION_WEIGHTS[QualityDimension.ACTIONABILITY]
            )
            
            result = QuestionQualityScore(
                overall=round(overall, 2),
                relevance=scores.get("relevance", 5),
                clarity=scores.get("clarity", 5),
                difficulty=scores.get("difficulty", 5),
                uniqueness=scores.get("uniqueness", 5),
                depth=scores.get("depth", 5),
                actionability=scores.get("actionability", 5),
                critique=critique if critique and critique.lower() != "none" else "",
                suggestions=[suggestion] if suggestion and suggestion.lower() != "none" else [],
                passed=overall >= self.MIN_QUALITY_THRESHOLD
            )
            
            self.evaluation_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            return self._evaluate_heuristic(question, topic, previous_questions, target_difficulty)
    
    def get_average_score(self) -> float:
        """Get average quality score across all evaluated questions."""
        if not self.evaluation_history:
            return 0.0
        return sum(r.overall for r in self.evaluation_history) / len(self.evaluation_history)
    
    def get_pass_rate(self) -> float:
        """Get percentage of questions that passed quality threshold."""
        if not self.evaluation_history:
            return 0.0
        passed = sum(1 for r in self.evaluation_history if r.passed)
        return passed / len(self.evaluation_history)
    
    def clear_history(self):
        """Clear evaluation history."""
        self.evaluation_history = []


# Singleton instance
_evaluator_instance: Optional[QuestionEvaluator] = None

def get_question_evaluator(use_llm: bool = False, llm=None) -> QuestionEvaluator:
    """Get or create singleton evaluator instance."""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = QuestionEvaluator(use_llm=use_llm, llm=llm)
    return _evaluator_instance
