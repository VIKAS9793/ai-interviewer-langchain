"""
Red Team Agent - Adversarial Critic Module

Part of TTD (Test-Time Diffusion) Algorithm Implementation.
Attacks questions to find logical flaws, biases, and weaknesses.

Architecture:
    Supervisor → Parallel Generators → [Red Team] → Evaluator → Refinement

Reference:
    TTD-DR uses "Red Team Agent" to attack drafts and find hidden flaws.
    This provides structured feedback for self-correction.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Types of attacks the Red Team can perform."""
    REPETITION = "repetition"  # Similar to previous questions
    AMBIGUITY = "ambiguity"  # Unclear or vague
    BIAS = "bias"  # Potentially discriminatory
    DIFFICULTY_MISMATCH = "difficulty_mismatch"  # Wrong level
    OFF_TOPIC = "off_topic"  # Not relevant to interview topic
    LEADING = "leading"  # Suggests the answer
    UNFAIR = "unfair"  # Requires knowledge candidate couldn't have
    TOO_BROAD = "too_broad"  # Impossible to answer fully
    TOO_NARROW = "too_narrow"  # Trivial answer


@dataclass
class CritiqueResult:
    """
    Result of Red Team attack on a question.
    
    Higher severity = worse problem that needs fixing.
    """
    severity: int = 0  # 1-10 (10 = critical flaw, must fix)
    attack_type: AttackType = AttackType.AMBIGUITY
    concern: str = ""  # What's wrong
    evidence: str = ""  # Why this is a problem
    recommendation: str = ""  # How to fix
    passed: bool = True  # Did question survive the attack?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "severity": self.severity,
            "attack_type": self.attack_type.value,
            "concern": self.concern,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "passed": self.passed
        }


class RedTeamAgent:
    """
    Adversarial critic that attacks questions to find flaws.
    
    Implements TTD's Red Team component:
    - Systematically challenges question quality
    - Finds logical flaws, biases, ambiguities
    - Provides structured feedback for refinement
    
    Attack Strategy:
    1. Run multiple attack types in sequence
    2. Return the most severe issue found
    3. If severity > threshold, question fails
    """
    
    # Threshold above which question fails
    SEVERITY_THRESHOLD = 5
    
    def __init__(self, use_llm: bool = False, llm=None):
        """
        Initialize Red Team agent.
        
        Args:
            use_llm: If True, use LLM for more sophisticated attacks
            llm: LLM instance for LLM-based attacks
        """
        self.use_llm = use_llm
        self.llm = llm
        self.attack_history: List[CritiqueResult] = []
        
        logger.info(f"🔴 RedTeamAgent initialized (use_llm={use_llm})")
    
    def attack(
        self, 
        question: str, 
        topic: str,
        previous_questions: Optional[List[str]] = None,
        target_difficulty: str = "medium"
    ) -> CritiqueResult:
        """
        Attack a question to find flaws.
        
        Runs multiple attack types and returns the most severe issue.
        
        Args:
            question: The question to attack
            topic: Interview topic for context
            previous_questions: Previous questions asked
            target_difficulty: Expected difficulty level
            
        Returns:
            CritiqueResult with the most severe issue found
        """
        previous_questions = previous_questions or []
        
        # Run all attacks
        critiques = [
            self._attack_repetition(question, previous_questions),
            self._attack_ambiguity(question),
            self._attack_bias(question),
            self._attack_relevance(question, topic),
            self._attack_difficulty(question, target_difficulty),
            self._attack_structure(question),
        ]
        
        # Find most severe
        worst = max(critiques, key=lambda c: c.severity)
        
        # Store in history
        self.attack_history.append(worst)
        
        # Log result
        if worst.passed:
            logger.info(f"🛡️ Question survived Red Team attack (severity: {worst.severity})")
        else:
            logger.warning(f"⚔️ Red Team found issue (severity: {worst.severity}): {worst.concern}")
        
        return worst
    
    def _attack_repetition(self, question: str, previous_questions: List[str]) -> CritiqueResult:
        """Attack: Check for semantic repetition."""
        if not previous_questions:
            return CritiqueResult(
                severity=0,
                attack_type=AttackType.REPETITION,
                concern="No previous questions to compare",
                passed=True
            )
        
        try:
            from src.ai_interviewer.modules.semantic_dedup import SemanticDeduplicator
            dedup = SemanticDeduplicator(similarity_threshold=0.70)
            
            is_dup, score = dedup.is_duplicate(question, previous_questions, return_score=True)
            
            if is_dup:
                return CritiqueResult(
                    severity=9,  # High severity - repetition is critical
                    attack_type=AttackType.REPETITION,
                    concern="Question is semantically similar to a previous question",
                    evidence=f"Similarity score: {score:.2f} (threshold: 0.70)",
                    recommendation="Generate a question on a completely different aspect of the topic",
                    passed=False
                )
            elif score > 0.5:  # Warning level
                return CritiqueResult(
                    severity=4,
                    attack_type=AttackType.REPETITION,
                    concern="Question has moderate similarity to previous questions",
                    evidence=f"Similarity score: {score:.2f}",
                    recommendation="Consider exploring a different angle",
                    passed=True
                )
            else:
                return CritiqueResult(
                    severity=0,
                    attack_type=AttackType.REPETITION,
                    concern="Question is unique",
                    passed=True
                )
        except Exception as e:
            logger.warning(f"Repetition attack failed: {e}")
            return CritiqueResult(severity=0, attack_type=AttackType.REPETITION, passed=True)
    
    def _attack_ambiguity(self, question: str) -> CritiqueResult:
        """Attack: Check for unclear or vague questions."""
        question_lower = question.lower()
        
        # Vague words that indicate ambiguity
        vague_words = ["stuff", "things", "something", "somehow", "etc", "whatever"]
        found_vague = [w for w in vague_words if w in question_lower]
        
        if found_vague:
            return CritiqueResult(
                severity=6,
                attack_type=AttackType.AMBIGUITY,
                concern="Question contains vague language",
                evidence=f"Vague words found: {', '.join(found_vague)}",
                recommendation="Replace vague terms with specific technical terminology",
                passed=False
            )
        
        # Check if question is too short
        word_count = len(question.split())
        if word_count < 5:
            return CritiqueResult(
                severity=5,
                attack_type=AttackType.AMBIGUITY,
                concern="Question is too brief to be clear",
                evidence=f"Only {word_count} words",
                recommendation="Add context or specifics to make the question clearer",
                passed=False
            )
        
        # Check for question mark
        if "?" not in question:
            return CritiqueResult(
                severity=3,
                attack_type=AttackType.AMBIGUITY,
                concern="Not clearly formatted as a question",
                recommendation="Add a question mark or rephrase as a direct question",
                passed=True
            )
        
        return CritiqueResult(severity=0, attack_type=AttackType.AMBIGUITY, passed=True)
    
    def _attack_bias(self, question: str) -> CritiqueResult:
        """Attack: Check for biased or discriminatory content."""
        question_lower = question.lower()
        
        # Check for discriminatory patterns
        discriminatory_patterns = [
            ("age", "Age discrimination"),
            ("gender", "Gender bias"),
            ("race", "Racial bias"),
            ("religion", "Religious discrimination"),
            ("nationality", "National origin discrimination"),
            ("married", "Marital status discrimination"),
            ("children", "Family status discrimination"),
            ("disability", "Disability discrimination"),
        ]
        
        # Technical contexts where these words are OK
        technical_contexts = ["age of data", "race condition", "child process", "child node"]
        
        for pattern, concern_type in discriminatory_patterns:
            if pattern in question_lower:
                # Check if it's a technical context
                if any(ctx in question_lower for ctx in technical_contexts):
                    continue
                    
                return CritiqueResult(
                    severity=10,  # Critical - potential legal issue
                    attack_type=AttackType.BIAS,
                    concern=f"Potentially discriminatory: {concern_type}",
                    evidence=f"Contains word '{pattern}'",
                    recommendation="Remove or rephrase to focus only on technical skills",
                    passed=False
                )
        
        return CritiqueResult(severity=0, attack_type=AttackType.BIAS, passed=True)
    
    def _attack_relevance(self, question: str, topic: str) -> CritiqueResult:
        """Attack: Check if question is relevant to the topic."""
        question_lower = question.lower()
        topic_lower = topic.lower()
        
        topic_words = set(topic_lower.split())
        question_words = set(question_lower.split())
        
        # Remove common words
        common_words = {"the", "a", "an", "is", "are", "how", "what", "why", "and", "or", "to", "in", "for"}
        topic_words = topic_words - common_words
        question_words = question_words - common_words
        
        overlap = topic_words & question_words
        
        if len(overlap) == 0 and len(topic_words) > 0:
            return CritiqueResult(
                severity=7,
                attack_type=AttackType.OFF_TOPIC,
                concern="Question appears unrelated to the topic",
                evidence=f"No overlap between topic '{topic}' and question",
                recommendation=f"Include relevant concepts from {topic}",
                passed=False
            )
        
        return CritiqueResult(severity=0, attack_type=AttackType.OFF_TOPIC, passed=True)
    
    def _attack_difficulty(self, question: str, target_difficulty: str) -> CritiqueResult:
        """Attack: Check if difficulty matches expectation."""
        question_lower = question.lower()
        
        difficulty_markers = {
            "easy": ["what is", "define", "list", "name"],
            "medium": ["how", "explain", "compare", "when"],
            "hard": ["design", "optimize", "architect", "scale", "trade-off", "debug complex"]
        }
        
        detected = "medium"  # Default
        for level, markers in difficulty_markers.items():
            if any(marker in question_lower for marker in markers):
                detected = level
                break
        
        # Calculate severity based on mismatch
        levels = ["easy", "medium", "hard"]
        target_idx = levels.index(target_difficulty) if target_difficulty in levels else 1
        detected_idx = levels.index(detected)
        
        diff = abs(target_idx - detected_idx)
        
        if diff == 0:
            return CritiqueResult(severity=0, attack_type=AttackType.DIFFICULTY_MISMATCH, passed=True)
        elif diff == 1:
            return CritiqueResult(
                severity=3,
                attack_type=AttackType.DIFFICULTY_MISMATCH,
                concern=f"Slight difficulty mismatch: expected {target_difficulty}, detected {detected}",
                recommendation="Consider adjusting the technical depth",
                passed=True
            )
        else:
            return CritiqueResult(
                severity=6,
                attack_type=AttackType.DIFFICULTY_MISMATCH,
                concern=f"Significant difficulty mismatch: expected {target_difficulty}, detected {detected}",
                recommendation=f"Rephrase to match {target_difficulty} level",
                passed=False
            )
    
    def _attack_structure(self, question: str) -> CritiqueResult:
        """Attack: Check question structure and format."""
        word_count = len(question.split())
        
        if word_count > 75:
            return CritiqueResult(
                severity=5,
                attack_type=AttackType.TOO_BROAD,
                concern="Question is too long and may be confusing",
                evidence=f"{word_count} words",
                recommendation="Break into smaller, focused questions",
                passed=False
            )
        
        if word_count < 3:
            return CritiqueResult(
                severity=5,
                attack_type=AttackType.TOO_NARROW,
                concern="Question is too short to be meaningful",
                evidence=f"Only {word_count} words",
                recommendation="Add context and specifics",
                passed=False
            )
        
        return CritiqueResult(severity=0, attack_type=AttackType.TOO_BROAD, passed=True)
    
    def get_attack_summary(self) -> Dict[str, Any]:
        """Get summary of all attacks performed."""
        if not self.attack_history:
            return {"total": 0, "passed": 0, "failed": 0}
        
        passed = sum(1 for c in self.attack_history if c.passed)
        failed = len(self.attack_history) - passed
        
        # Count by attack type
        by_type = {}
        for c in self.attack_history:
            attack_name = c.attack_type.value
            if attack_name not in by_type:
                by_type[attack_name] = {"count": 0, "failed": 0}
            by_type[attack_name]["count"] += 1
            if not c.passed:
                by_type[attack_name]["failed"] += 1
        
        return {
            "total": len(self.attack_history),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(self.attack_history),
            "by_type": by_type
        }
    
    def clear_history(self):
        """Clear attack history."""
        self.attack_history = []


# Singleton instance
_red_team_instance: Optional[RedTeamAgent] = None

def get_red_team_agent(use_llm: bool = False, llm=None) -> RedTeamAgent:
    """Get or create singleton Red Team agent."""
    global _red_team_instance
    if _red_team_instance is None:
        _red_team_instance = RedTeamAgent(use_llm=use_llm, llm=llm)
    return _red_team_instance
