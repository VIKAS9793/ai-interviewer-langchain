"""
Reflect Agent: Quality Assurance and Self-Evaluation System

This module implements an independent evaluator that verifies the quality,
fairness, and consistency of interview questions and evaluations. It acts
as a third-party supervisor to detect and correct potential issues.

Research Reference:
    [1] "Learning on the Job: An Experience-Driven, Self-Evolving Agent"
        arXiv:2510.08002 (2025)
        https://arxiv.org/abs/2510.08002
        Section 3.4 "Reflect Agent"
    
    [2] "Towards autonomous normative multi-agent systems"
        arXiv:2512.02329 (2025)
        https://arxiv.org/abs/2512.02329
        Research Direction 2: Self-regulation and compliance
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReflectionOutcome(Enum):
    """Outcome of a reflection check."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass
class ReflectionResult:
    """
    Result of a reflection/evaluation check.
    
    Based on MUSE's Reflect Agent evaluation output.
    Reference: arXiv:2510.08002, Section 3.4
    """
    outcome: ReflectionOutcome
    dimension: str  # "fairness", "consistency", "truthfulness", etc.
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SOP:
    """
    Standard Operating Procedure extracted from successful interview.
    
    Represents procedural memory in MUSE's memory hierarchy.
    Reference: arXiv:2510.08002, Section 3.2 "Memory Module"
    """
    title: str
    topic: str
    steps: List[str]
    success_rate: float = 0.0
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ReflectAgent:
    """
    Independent third-party supervisor for interview quality assurance.
    
    Implements MUSE's Reflect Agent concept with three core evaluation dimensions:
    1. Truthfulness Verification - Ensure conclusions are grounded
    2. Fairness Verification - Check for bias and discrimination
    3. Consistency Verification - Ensure scoring is consistent
    
    Research Reference: arXiv:2510.08002, Section 3.4 "Reflect Agent"
    """
    
    def __init__(self):
        """Initialize the Reflect Agent."""
        self.reflection_history: List[ReflectionResult] = []
        self.extracted_sops: List[SOP] = []
        
        # Configurable thresholds
        self.config = {
            "min_score_justification_length": 20,
            "score_consistency_tolerance": 2.0,
            "extreme_score_threshold": (2, 9),
        }
        
        logger.info("🔍 ReflectAgent initialized for quality assurance")
    
    # =========================================================================
    # FAIRNESS VERIFICATION
    # =========================================================================
    
    def evaluate_question_fairness(
        self, 
        question: str, 
        topic: str,
        candidate_context: Optional[Dict] = None
    ) -> ReflectionResult:
        """
        Evaluate if a question is fair and appropriate.
        
        Checks for:
        - Discriminatory content
        - Personal/invasive questions
        - Topic relevance
        - Appropriate difficulty context
        
        Reference: arXiv:2512.02329, Research Direction 2 (Self-regulation)
        """
        issues = []
        recommendations = []
        question_lower = question.lower()
        
        # Check for discriminatory patterns
        discriminatory_patterns = [
            "age", "gender", "race", "religion", "nationality",
            "married", "children", "pregnant", "disability",
            "political", "sexual orientation"
        ]
        
        for pattern in discriminatory_patterns:
            if pattern in question_lower:
                # Context matters - some are OK in technical contexts
                if not self._is_technical_context(question, pattern):
                    issues.append(f"Potentially discriminatory: contains '{pattern}'")
                    recommendations.append(
                        f"Remove or rephrase content related to '{pattern}'"
                    )
        
        # Check for personal/invasive questions
        personal_patterns = [
            "salary", "how much do you make", "personal life",
            "family situation", "health condition"
        ]
        
        for pattern in personal_patterns:
            if pattern in question_lower:
                issues.append(f"Personal/invasive content: '{pattern}'")
                recommendations.append("Focus on technical skills only")
        
        # Check topic relevance
        topic_words = set(topic.lower().split())
        question_words = set(question_lower.split())
        relevance = len(topic_words & question_words) / max(1, len(topic_words))
        
        if relevance < 0.1 and len(question) > 50:
            issues.append("Question may not be relevant to topic")
            recommendations.append(f"Ensure question is related to {topic}")
        
        # Determine outcome
        if issues:
            outcome = (
                ReflectionOutcome.FAILED if len(issues) > 1 
                else ReflectionOutcome.WARNING
            )
        else:
            outcome = ReflectionOutcome.PASSED
        
        result = ReflectionResult(
            outcome=outcome,
            dimension="question_fairness",
            message=f"Question fairness: {len(issues)} issues found",
            details={
                "issues": issues,
                "topic": topic,
                "question_preview": question[:100]
            },
            recommendations=recommendations
        )
        
        self._log_reflection(result)
        return result
    
    def _is_technical_context(self, question: str, pattern: str) -> bool:
        """Check if pattern usage is in technical context."""
        technical_contexts = {
            "age": ["age of data", "age of cache", "garbage collection age"],
            "race": ["race condition", "data race"],
            "children": ["child process", "child node", "child element"],
            "gender": ["gender field", "form validation"]
        }
        
        question_lower = question.lower()
        contexts = technical_contexts.get(pattern, [])
        return any(ctx in question_lower for ctx in contexts)
    
    # =========================================================================
    # CONSISTENCY VERIFICATION
    # =========================================================================
    
    def evaluate_scoring_consistency(
        self,
        answer: str,
        score: float,
        justification: str,
        topic: str,
        previous_scores: Optional[List[float]] = None
    ) -> ReflectionResult:
        """
        Verify scoring consistency and justification quality.
        
        Checks for:
        - Adequate justification for score
        - Extreme scores require strong justification
        - Consistency with previous scoring patterns
        
        Reference: arXiv:2510.08002, Section 3.4 "Sub-task Evaluation"
        """
        issues = []
        recommendations = []
        
        # Check justification length
        if len(justification) < self.config["min_score_justification_length"]:
            issues.append("Justification is too brief")
            recommendations.append(
                "Provide more detailed reasoning for the score"
            )
        
        # Check extreme scores
        low_thresh, high_thresh = self.config["extreme_score_threshold"]
        if score <= low_thresh or score >= high_thresh:
            if len(justification) < 50:
                issues.append(
                    f"Extreme score ({score}) requires detailed justification"
                )
                recommendations.append(
                    "Extreme scores need comprehensive explanation"
                )
        
        # Check score-content alignment
        answer_length = len(answer.split())
        if score >= 8 and answer_length < 20:
            issues.append("High score for very brief answer")
            recommendations.append(
                "Verify if brief answer truly demonstrates expertise"
            )
        
        if score <= 3 and answer_length > 100:
            issues.append("Low score for detailed answer - verify assessment")
            recommendations.append(
                "Re-evaluate: detailed answers may show partial understanding"
            )
        
        # Check consistency with previous scores
        if previous_scores and len(previous_scores) >= 3:
            avg_score = sum(previous_scores) / len(previous_scores)
            tolerance = self.config["score_consistency_tolerance"]
            
            if abs(score - avg_score) > tolerance * 2:
                issues.append(
                    f"Score ({score}) deviates significantly from "
                    f"average ({avg_score:.1f})"
                )
                recommendations.append(
                    "Review if scoring criteria changed mid-interview"
                )
        
        # Determine outcome
        if issues:
            outcome = (
                ReflectionOutcome.FAILED if len(issues) > 2
                else ReflectionOutcome.WARNING
            )
        else:
            outcome = ReflectionOutcome.PASSED
        
        result = ReflectionResult(
            outcome=outcome,
            dimension="scoring_consistency",
            message=f"Scoring check: {len(issues)} issues found",
            details={
                "score": score,
                "justification_length": len(justification),
                "answer_length": answer_length,
                "issues": issues
            },
            recommendations=recommendations
        )
        
        self._log_reflection(result)
        return result
    
    # =========================================================================
    # TRUTHFULNESS VERIFICATION
    # =========================================================================
    
    def verify_truthfulness(
        self,
        claim: str,
        evidence: List[str],
        context: str
    ) -> ReflectionResult:
        """
        Verify that claims are grounded in evidence.
        
        Checks for:
        - Claims have supporting evidence
        - Conclusions follow from observations
        
        Reference: arXiv:2510.08002, Section 3.4 "Truthfulness Verification"
        """
        issues = []
        recommendations = []
        
        claim_lower = claim.lower()
        
        # Check if claim has any evidence
        if not evidence:
            issues.append("Claim made without supporting evidence")
            recommendations.append("Provide specific examples or observations")
        
        # Check evidence relevance
        claim_words = set(claim_lower.split())
        total_overlap = 0
        
        for ev in evidence:
            ev_words = set(ev.lower().split())
            overlap = len(claim_words & ev_words)
            total_overlap += overlap
        
        if evidence and total_overlap < 2:
            issues.append("Evidence may not support the claim")
            recommendations.append("Ensure evidence directly relates to claim")
        
        # Determine outcome
        if not issues:
            outcome = ReflectionOutcome.PASSED
        elif len(issues) == 1:
            outcome = ReflectionOutcome.WARNING
        else:
            outcome = ReflectionOutcome.FAILED
        
        result = ReflectionResult(
            outcome=outcome,
            dimension="truthfulness",
            message=f"Truthfulness check: {len(issues)} issues",
            details={
                "claim_preview": claim[:100],
                "evidence_count": len(evidence),
                "issues": issues
            },
            recommendations=recommendations
        )
        
        self._log_reflection(result)
        return result
    
    # =========================================================================
    # SOP EXTRACTION
    # =========================================================================
    
    def extract_sop(
        self,
        session_id: str,
        topic: str,
        questions: List[Dict],
        evaluations: List[Dict],
        final_score: float,
        success_threshold: float = 7.0
    ) -> Optional[SOP]:
        """
        Extract Standard Operating Procedure from successful interview.
        
        Creates procedural memory for future interview guidance.
        
        Reference: arXiv:2510.08002, Section 3.4 "Memory Update Mechanism"
        """
        if final_score < success_threshold:
            logger.debug(
                f"Score {final_score} below threshold {success_threshold}, "
                f"no SOP extracted"
            )
            return None
        
        # Extract question progression
        steps = []
        
        for i, (q, e) in enumerate(zip(questions, evaluations), 1):
            q_text = q.get('question', 'Question')[:50]
            q_difficulty = q.get('difficulty', 'medium')
            e_score = e.get('overall_score', 5)
            
            step = (
                f"Step {i}: Ask {q_difficulty} question about "
                f"{q_text}... (expected score: {e_score})"
            )
            steps.append(step)
        
        # Add summary step
        steps.append(
            f"Summary: This {len(questions)}-question flow achieved "
            f"score {final_score:.1f}"
        )
        
        sop = SOP(
            title=f"Successful {topic} Interview Flow",
            topic=topic,
            steps=steps,
            success_rate=final_score / 10.0
        )
        
        self.extracted_sops.append(sop)
        
        logger.info(f"📋 Extracted SOP: {sop.title}")
        return sop
    
    # =========================================================================
    # COMPREHENSIVE REFLECTION
    # =========================================================================
    
    def reflect_on_interview(
        self,
        questions: List[str],
        answers: List[str],
        scores: List[float],
        justifications: List[str],
        topic: str
    ) -> Dict[str, Any]:
        """
        Comprehensive reflection on entire interview session.
        
        Returns aggregated quality assessment.
        
        Reference: arXiv:2510.08002, Section 3.4 "Reflect Agent"
        """
        results: Dict[str, Any] = {
            "question_fairness": [],
            "scoring_consistency": [],
            "overall_quality": ReflectionOutcome.PASSED,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        # Type annotations for mypy
        question_fairness: List[str] = results["question_fairness"]  # type: ignore[assignment]
        scoring_consistency: List[str] = results["scoring_consistency"]  # type: ignore[assignment]
        recommendations: List[str] = results["recommendations"]  # type: ignore[assignment]
        
        failed_count = 0
        warning_count = 0
        
        # Evaluate each question
        for q in questions:
            r = self.evaluate_question_fairness(q, topic)
            question_fairness.append(r.outcome.value)
            if r.outcome == ReflectionOutcome.FAILED:
                failed_count += 1
            elif r.outcome == ReflectionOutcome.WARNING:
                warning_count += 1
            recommendations.extend(r.recommendations)
        
        # Evaluate each score
        for i, (ans, score, just) in enumerate(
            zip(answers, scores, justifications)
        ):
            prev_scores = scores[:i] if i > 0 else None
            r = self.evaluate_scoring_consistency(
                ans, score, just, topic, prev_scores
            )
            scoring_consistency.append(r.outcome.value)
            if r.outcome == ReflectionOutcome.FAILED:
                failed_count += 1
            elif r.outcome == ReflectionOutcome.WARNING:
                warning_count += 1
            recommendations.extend(r.recommendations)
        
        # Determine overall quality
        if failed_count > 0:
            results["overall_quality"] = ReflectionOutcome.FAILED
        elif warning_count > 2:
            results["overall_quality"] = ReflectionOutcome.WARNING
        
        # Deduplicate recommendations
        results["recommendations"] = list(set(recommendations))
        results["question_fairness"] = question_fairness
        results["scoring_consistency"] = scoring_consistency
        
        logger.info(
            f"🔍 Interview reflection: {results['overall_quality'].value} "
            f"({failed_count} failed, {warning_count} warnings)"
        )
        
        return results
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _log_reflection(self, result: ReflectionResult):
        """Log reflection result to history."""
        self.reflection_history.append(result)
        
        # Log to console
        icon = {
            ReflectionOutcome.PASSED: "✅",
            ReflectionOutcome.WARNING: "⚠️",
            ReflectionOutcome.FAILED: "❌"
        }[result.outcome]
        
        logger.debug(f"{icon} {result.dimension}: {result.message}")
    
    def get_reflection_summary(self) -> Dict[str, Any]:
        """Get summary of all reflections."""
        if not self.reflection_history:
            return {"total": 0, "passed": 0, "warnings": 0, "failed": 0}
        
        passed = sum(
            1 for r in self.reflection_history 
            if r.outcome == ReflectionOutcome.PASSED
        )
        warnings = sum(
            1 for r in self.reflection_history 
            if r.outcome == ReflectionOutcome.WARNING
        )
        failed = sum(
            1 for r in self.reflection_history 
            if r.outcome == ReflectionOutcome.FAILED
        )
        
        return {
            "total": len(self.reflection_history),
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "pass_rate": passed / len(self.reflection_history),
            "sops_extracted": len(self.extracted_sops)
        }
    
    def clear_history(self):
        """Clear reflection history."""
        self.reflection_history = []
        logger.info("🧹 Reflection history cleared")
