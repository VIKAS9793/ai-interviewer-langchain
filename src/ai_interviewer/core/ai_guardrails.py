"""
AI Guardrails, Explainability, and Accountability Module

This module ensures AI decisions are:
- EXPLAINABLE: Clear reasoning trails for all decisions
- RESPONSIBLE: Bias detection and fair evaluation
- ACCOUNTABLE: Complete audit logs and decision tracking
- SAFE: Content filtering and safety guardrails

Implements MAANG-level responsible AI practices.
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety classification levels"""
    SAFE = "safe"
    CAUTION = "caution"
    BLOCKED = "blocked"


class BiasCategory(Enum):
    """Types of potential bias"""
    GENDER = "gender"
    AGE = "age"
    ETHNICITY = "ethnicity"
    EDUCATION = "education"
    LANGUAGE = "language"
    NONE = "none"


@dataclass
class DecisionAudit:
    """Complete audit record of an AI decision"""
    decision_id: str
    timestamp: datetime
    action_type: str
    input_summary: str
    reasoning_chain: List[Dict[str, Any]]
    output_summary: str
    confidence: float
    safety_check: Dict[str, Any]
    bias_check: Dict[str, Any]
    human_readable_explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailResult:
    """Result of guardrail evaluation"""
    passed: bool
    safety_level: SafetyLevel
    issues: List[str]
    recommendations: List[str]
    explanation: str


class AIGuardrails:
    """
    AI Safety Guardrails
    
    Ensures safe, fair, and responsible AI behavior through:
    - Content safety filtering
    - Bias detection
    - Fairness checks
    - Output validation
    """
    
    def __init__(self):
        # Harmful content patterns
        self._harmful_patterns = [
            r'\b(discriminat|prejudic|bias against)\b',
            r'\b(cheat|hack|illegal|exploit)\b',
            r'\b(personal attack|insult|demean)\b',
        ]
        
        # Bias indicator words
        self._bias_indicators = {
            BiasCategory.GENDER: [
                "he should", "she should", "men are", "women are",
                "typical for a man", "typical for a woman"
            ],
            BiasCategory.AGE: [
                "too old", "too young", "senior developer",
                "fresh graduate", "experienced means older"
            ],
            BiasCategory.EDUCATION: [
                "only from top schools", "self-taught can't",
                "must have degree", "bootcamp graduates"
            ]
        }
        
        # Evaluation fairness thresholds
        self._fairness_config = {
            "min_score": 1,
            "max_score": 10,
            "score_variance_threshold": 3.0,
            "require_justification_above": 8,
            "require_justification_below": 4
        }
        
        logger.info("🛡️ AI Guardrails initialized")
    
    def check_content_safety(self, content: str) -> GuardrailResult:
        """Check content for harmful or inappropriate material"""
        issues = []
        recommendations = []
        
        content_lower = content.lower()
        
        # Check for harmful patterns
        for pattern in self._harmful_patterns:
            if re.search(pattern, content_lower):
                issues.append(f"Potentially harmful content detected: {pattern}")
        
        # Check for excessive negativity
        negative_words = ["terrible", "awful", "horrible", "incompetent", "useless"]
        negative_count = sum(1 for word in negative_words if word in content_lower)
        if negative_count > 2:
            issues.append("Excessive negative language detected")
            recommendations.append("Consider more constructive phrasing")
        
        # Determine safety level
        if len(issues) > 2:
            safety_level = SafetyLevel.BLOCKED
        elif len(issues) > 0:
            safety_level = SafetyLevel.CAUTION
        else:
            safety_level = SafetyLevel.SAFE
        
        return GuardrailResult(
            passed=safety_level != SafetyLevel.BLOCKED,
            safety_level=safety_level,
            issues=issues,
            recommendations=recommendations,
            explanation=self._generate_safety_explanation(issues)
        )
    
    def check_evaluation_fairness(self, evaluation: Dict[str, Any],
                                  context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """Check if evaluation is fair and unbiased"""
        issues = []
        recommendations = []
        score = evaluation.get("score", 5)
        feedback = evaluation.get("feedback", "") or evaluation.get("brief_feedback", "")
        
        # Score range validation
        if score < self._fairness_config["min_score"] or score > self._fairness_config["max_score"]:
            issues.append(f"Score {score} outside valid range")
        
        # Justification requirement for extreme scores
        if score >= self._fairness_config["require_justification_above"]:
            if not feedback or len(feedback) < 20:
                issues.append("High score requires detailed justification")
                recommendations.append("Provide specific examples that justify high score")
        
        if score <= self._fairness_config["require_justification_below"]:
            if not feedback or len(feedback) < 20:
                issues.append("Low score requires detailed justification")
                recommendations.append("Provide specific feedback for improvement")
        
        # Check for bias in feedback
        bias_result = self._detect_bias(feedback)
        if bias_result["detected"]:
            issues.extend(bias_result["issues"])
            recommendations.append("Review feedback for potential bias")
        
        # Consistency check (if history provided)
        if context and "performance_history" in context:
            history = context["performance_history"]
            if history and len(history) >= 2:
                variance = abs(score - sum(history) / len(history))
                if variance > self._fairness_config["score_variance_threshold"]:
                    issues.append(f"Score variance ({variance:.1f}) exceeds threshold")
                    recommendations.append("Ensure scoring consistency")
        
        safety_level = SafetyLevel.CAUTION if issues else SafetyLevel.SAFE
        
        return GuardrailResult(
            passed=len(issues) == 0,
            safety_level=safety_level,
            issues=issues,
            recommendations=recommendations,
            explanation=self._generate_fairness_explanation(issues, score)
        )
    
    def check_question_fairness(self, question: str, topic: str) -> GuardrailResult:
        """Check if interview question is fair and appropriate"""
        issues = []
        recommendations = []
        question_lower = question.lower()
        
        # Check for personal/discriminatory questions
        personal_patterns = [
            r'\b(married|children|family|pregnant)\b',
            r'\b(age|old are you|born)\b',
            r'\b(religion|religious|church)\b',
            r'\b(political|vote|party)\b',
            r'\b(salary|compensation) expectation\b',
        ]
        
        for pattern in personal_patterns:
            if re.search(pattern, question_lower):
                issues.append(f"Potentially discriminatory question topic: {pattern}")
        
        # Check if question is relevant to topic
        topic_keywords = self._get_topic_keywords(topic)
        relevant = any(kw.lower() in question_lower for kw in topic_keywords[:5])
        if not relevant:
            issues.append("Question may not be relevant to interview topic")
            recommendations.append(f"Ensure question relates to {topic}")
        
        # Check question clarity
        if len(question.split()) < 5:
            issues.append("Question may be too brief")
            recommendations.append("Provide more context in the question")
        
        if len(question.split()) > 100:
            issues.append("Question may be too long")
            recommendations.append("Consider breaking into smaller questions")
        
        safety_level = SafetyLevel.BLOCKED if any("discriminatory" in i for i in issues) else (
            SafetyLevel.CAUTION if issues else SafetyLevel.SAFE
        )
        
        return GuardrailResult(
            passed=safety_level == SafetyLevel.SAFE,
            safety_level=safety_level,
            issues=issues,
            recommendations=recommendations,
            explanation=self._generate_question_explanation(issues)
        )
    
    def _detect_bias(self, text: str) -> Dict[str, Any]:
        """Detect potential bias in text"""
        text_lower = text.lower()
        detected_biases = []
        issues = []
        
        for category, indicators in self._bias_indicators.items():
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    detected_biases.append(category.value)
                    issues.append(f"Potential {category.value} bias detected: '{indicator}'")
        
        return {
            "detected": len(detected_biases) > 0,
            "categories": list(set(detected_biases)),
            "issues": issues
        }
    
    def _get_topic_keywords(self, topic: str) -> List[str]:
        """Get relevant keywords for topic"""
        keywords = {
            "JavaScript/Frontend Development": [
                "javascript", "react", "vue", "angular", "dom", "css", "html",
                "typescript", "webpack", "node", "npm", "api", "async"
            ],
            "Python/Backend Development": [
                "python", "django", "flask", "fastapi", "database", "sql",
                "api", "rest", "async", "decorator", "class", "function"
            ],
            "Machine Learning/AI": [
                "model", "training", "algorithm", "data", "neural", "deep",
                "learning", "prediction", "classification", "tensorflow", "pytorch"
            ],
            "System Design": [
                "architecture", "scale", "database", "cache", "load",
                "microservice", "distributed", "latency", "availability"
            ]
        }
        return keywords.get(topic, ["technical", "programming", "software"])
    
    def _generate_safety_explanation(self, issues: List[str]) -> str:
        if not issues:
            return "Content passed all safety checks."
        return f"Safety review identified {len(issues)} concern(s): {'; '.join(issues[:2])}"
    
    def _generate_fairness_explanation(self, issues: List[str], score: float) -> str:
        if not issues:
            return f"Evaluation score of {score}/10 passed fairness checks."
        return f"Fairness review for score {score}/10: {'; '.join(issues[:2])}"
    
    def _generate_question_explanation(self, issues: List[str]) -> str:
        if not issues:
            return "Question passed all fairness and relevance checks."
        return f"Question review: {'; '.join(issues[:2])}"


class AIExplainability:
    """
    AI Explainability Engine
    
    Provides human-readable explanations for all AI decisions:
    - Why was this question asked?
    - Why was this score given?
    - What factors influenced the decision?
    """
    
    def __init__(self):
        self.explanation_templates = {
            "question_generation": "Generated {difficulty} question because: {reasons}",
            "evaluation": "Score of {score}/10 based on: {factors}",
            "adaptation": "Adapted approach due to: {triggers}",
            "conclusion": "Final assessment: {assessment}"
        }
        logger.info("💡 AI Explainability Engine initialized")
    
    def explain_question_choice(self, thought_chain: Dict[str, Any],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for why a question was chosen"""
        explanation = {
            "summary": "",
            "factors": [],
            "reasoning_steps": [],
            "confidence": thought_chain.get("confidence", 0.7),
            "human_readable": ""
        }
        
        # Extract reasoning steps
        thoughts = thought_chain.get("thoughts", [])
        for thought in thoughts:
            step = thought.get("step", "unknown")
            explanation["reasoning_steps"].append({
                "step": step,
                "description": thought.get("thought", "")
            })
        
        # Identify key factors
        approach = thought_chain.get("conclusion", "default")
        explanation["factors"] = self._identify_question_factors(approach, context)
        
        # Generate human-readable explanation
        explanation["summary"] = f"Selected '{approach}' approach"
        explanation["human_readable"] = self._generate_question_explanation_text(
            approach, explanation["factors"], context
        )
        
        return explanation
    
    def explain_evaluation(self, evaluation: Dict[str, Any],
                          answer: str, question: str) -> Dict[str, Any]:
        """Generate explanation for evaluation score"""
        score = evaluation.get("score", 5)
        
        explanation = {
            "summary": f"Score: {score}/10",
            "factors": [],
            "breakdown": {},
            "confidence": evaluation.get("confidence", 0.7),
            "human_readable": ""
        }
        
        # Break down scoring factors
        breakdown = {}
        if "technical_accuracy" in evaluation:
            breakdown["Technical Accuracy"] = evaluation["technical_accuracy"]
        if "understanding_depth" in evaluation:
            breakdown["Understanding"] = evaluation["understanding_depth"]
        if "communication" in evaluation:
            breakdown["Communication"] = evaluation["communication"]
        if "practical_application" in evaluation:
            breakdown["Practical Skills"] = evaluation["practical_application"]
        
        explanation["breakdown"] = breakdown
        
        # Identify contributing factors
        factors = []
        word_count = len(answer.split())
        if word_count > 50:
            factors.append("Detailed response provided")
        elif word_count < 20:
            factors.append("Brief response")
        
        if evaluation.get("strengths"):
            factors.extend([f"Strength: {s}" for s in evaluation["strengths"][:2]])
        if evaluation.get("improvements"):
            factors.extend([f"Improvement area: {i}" for i in evaluation["improvements"][:2]])
        
        explanation["factors"] = factors
        
        # Generate human-readable explanation
        explanation["human_readable"] = self._generate_evaluation_explanation_text(
            score, breakdown, factors
        )
        
        return explanation
    
    def explain_adaptation(self, adaptation: Dict[str, Any],
                          candidate_state: str) -> Dict[str, Any]:
        """Explain why system adapted its behavior"""
        adaptations_made: List[str] = []
        
        # Document each adaptation
        if adaptation.get("difficulty_adjustment", 0) != 0:
            adj = adaptation["difficulty_adjustment"]
            adaptations_made.append(
                f"Difficulty {'increased' if adj > 0 else 'decreased'}"
            )
        
        if adaptation.get("tone_adjustment") and adaptation["tone_adjustment"] != "neutral":
            adaptations_made.append(
                f"Tone adjusted to: {adaptation['tone_adjustment']}"
            )
        
        if adaptation.get("support_level") and adaptation["support_level"] != "standard":
            adaptations_made.append(
                f"Support level: {adaptation['support_level']}"
            )
        
        # Generate rationale
        rationale = self._generate_adaptation_rationale(
            candidate_state, adaptations_made
        )
        
        explanation = {
            "trigger": candidate_state,
            "adaptations_made": adaptations_made,
            "rationale": rationale,
            "human_readable": ""
        }
        
        explanation["human_readable"] = (
            f"Detected candidate state: {candidate_state}. "
            f"Adaptations: {', '.join(adaptations_made) or 'None required'}."
        )
        
        return explanation
    
    def _identify_question_factors(self, approach: str,
                                   context: Dict[str, Any]) -> List[str]:
        """Identify factors that influenced question choice"""
        factors = []
        
        if approach == "gap_focused":
            gaps = context.get("knowledge_gaps", [])
            if gaps:
                factors.append(f"Targeting knowledge gap: {gaps[0]}")
        elif approach == "strength_building":
            strengths = context.get("strengths", [])
            if strengths:
                factors.append(f"Building on strength: {strengths[0]}")
        elif approach == "progressive_challenge":
            factors.append("Increasing difficulty progressively")
        
        # Add context factors
        if "performance_history" in context:
            history = context["performance_history"]
            if history:
                avg = sum(history) / len(history)
                factors.append(f"Average performance: {avg:.1f}/10")
        
        if "candidate_state" in context:
            factors.append(f"Candidate state: {context['candidate_state']}")
        
        return factors
    
    def _generate_question_explanation_text(self, approach: str,
                                           factors: List[str],
                                           context: Dict[str, Any]) -> str:
        """Generate human-readable question explanation"""
        text = f"This question was selected using the '{approach}' strategy. "
        
        if factors:
            text += f"Key factors: {'; '.join(factors[:3])}. "
        
        q_num = context.get("question_number", 1)
        max_q = context.get("max_questions", 5)
        text += f"(Question {q_num} of {max_q})"
        
        return text
    
    def _generate_evaluation_explanation_text(self, score: float,
                                             breakdown: Dict[str, float],
                                             factors: List[str]) -> str:
        """Generate human-readable evaluation explanation"""
        text = f"The answer received a score of {score}/10. "
        
        if breakdown:
            breakdown_text = ", ".join([
                f"{k}: {v:.1%}" if isinstance(v, float) and v <= 1 else f"{k}: {v}"
                for k, v in list(breakdown.items())[:3]
            ])
            text += f"Breakdown: {breakdown_text}. "
        
        if factors:
            text += f"Notable factors: {'; '.join(factors[:2])}."
        
        return text
    
    def _generate_adaptation_rationale(self, state: str,
                                       adaptations: List[str]) -> str:
        """Generate rationale for adaptations"""
        rationales = {
            "struggling": "Candidate appears to be having difficulty. Adjusting to provide more support.",
            "excelling": "Candidate is performing well. Increasing challenge level.",
            "nervous": "Candidate seems anxious. Adopting a more supportive tone.",
            "confident": "Candidate is comfortable. Maintaining current approach.",
            "improving": "Candidate is showing improvement. Recognizing progress.",
            "declining": "Performance declining. Providing additional support."
        }
        return rationales.get(state, "Continuing with standard approach.")


class AIAccountability:
    """
    AI Accountability System
    
    Maintains complete audit trail for all AI actions:
    - Decision logging
    - Action tracking
    - Compliance reporting
    """
    
    def __init__(self, max_audit_size: int = 1000):
        self.audit_log: List[DecisionAudit] = []
        self.max_audit_size = max_audit_size
        self._audit_lock = None
        
        # Metrics
        self.accountability_metrics = {
            "total_decisions": 0,
            "blocked_decisions": 0,
            "cautioned_decisions": 0,
            "bias_detections": 0
        }
        
        logger.info("📋 AI Accountability System initialized")
    
    def log_decision(self, action_type: str,
                    input_data: Dict[str, Any],
                    output_data: Dict[str, Any],
                    reasoning: Dict[str, Any],
                    safety_result: GuardrailResult,
                    explanation: Dict[str, Any]) -> str:
        """Log a complete decision audit"""
        decision_id = self._generate_decision_id()
        
        audit = DecisionAudit(
            decision_id=decision_id,
            timestamp=datetime.now(),
            action_type=action_type,
            input_summary=self._summarize_input(input_data),
            reasoning_chain=reasoning.get("thoughts", []),
            output_summary=self._summarize_output(output_data),
            confidence=reasoning.get("confidence", 0.0),
            safety_check={
                "passed": safety_result.passed,
                "level": safety_result.safety_level.value,
                "issues": safety_result.issues
            },
            bias_check={
                "issues_found": len([i for i in safety_result.issues if "bias" in i.lower()]),
                "recommendations": safety_result.recommendations
            },
            human_readable_explanation=explanation.get("human_readable", ""),
            metadata={
                "model": "autonomous_interviewer",
                "version": "2.0"
            }
        )
        
        # Add to log
        self.audit_log.append(audit)
        
        # Trim if needed
        if len(self.audit_log) > self.max_audit_size:
            self.audit_log = self.audit_log[-self.max_audit_size:]
        
        # Update metrics
        self.accountability_metrics["total_decisions"] += 1
        if not safety_result.passed:
            self.accountability_metrics["blocked_decisions"] += 1
        if safety_result.safety_level == SafetyLevel.CAUTION:
            self.accountability_metrics["cautioned_decisions"] += 1
        if any("bias" in i.lower() for i in safety_result.issues):
            self.accountability_metrics["bias_detections"] += 1
        
        return decision_id
    
    def get_decision_audit(self, decision_id: str) -> Optional[DecisionAudit]:
        """Retrieve specific decision audit"""
        for audit in self.audit_log:
            if audit.decision_id == decision_id:
                return audit
        return None
    
    def get_audit_summary(self, last_n: int = 10) -> Dict[str, Any]:
        """Get summary of recent audits"""
        recent = self.audit_log[-last_n:]
        
        return {
            "total_audits": len(self.audit_log),
            "recent_count": len(recent),
            "metrics": self.accountability_metrics,
            "recent_summaries": [
                {
                    "id": a.decision_id,
                    "action": a.action_type,
                    "timestamp": a.timestamp.isoformat(),
                    "confidence": a.confidence,
                    "safety_passed": a.safety_check["passed"]
                }
                for a in recent
            ]
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report for review"""
        total = self.accountability_metrics["total_decisions"]
        blocked = self.accountability_metrics["blocked_decisions"]
        bias = self.accountability_metrics["bias_detections"]
        
        return {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_decisions": total,
                "blocked_rate": blocked / total if total > 0 else 0,
                "bias_detection_rate": bias / total if total > 0 else 0,
                "compliance_score": 1.0 - (blocked / total) if total > 0 else 1.0
            },
            "details": self.accountability_metrics,
            "recommendations": self._generate_compliance_recommendations()
        }
    
    def _generate_decision_id(self) -> str:
        """Generate unique decision ID"""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _summarize_input(self, input_data: Dict[str, Any]) -> str:
        """Summarize input data for audit"""
        keys = list(input_data.keys())[:5]
        return f"Input keys: {', '.join(keys)}"
    
    def _summarize_output(self, output_data: Dict[str, Any]) -> str:
        """Summarize output data for audit"""
        if "question" in output_data:
            return f"Generated question: {output_data['question'][:50]}..."
        if "score" in output_data:
            return f"Evaluation score: {output_data['score']}"
        return str(output_data)[:100]
    
    def _generate_compliance_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        total = self.accountability_metrics["total_decisions"]
        
        if total == 0:
            return ["No decisions recorded yet"]
        
        blocked_rate = self.accountability_metrics["blocked_decisions"] / total
        if blocked_rate > 0.1:
            recommendations.append("High block rate - review content generation")
        
        bias_rate = self.accountability_metrics["bias_detections"] / total
        if bias_rate > 0.05:
            recommendations.append("Bias detections above threshold - review evaluation criteria")
        
        if not recommendations:
            recommendations.append("System operating within compliance parameters")
        
        return recommendations


# Unified interface
class ResponsibleAI:
    """
    Unified Responsible AI Interface
    
    Combines guardrails, explainability, and accountability into
    a single interface for the autonomous interviewer.
    """
    
    def __init__(self):
        self.guardrails = AIGuardrails()
        self.explainability = AIExplainability()
        self.accountability = AIAccountability()
        
        logger.info("🔒 Responsible AI System initialized")
    
    def validate_and_explain_question(self, question: str, topic: str,
                                      thought_chain: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question and provide explanation"""
        # Check guardrails
        safety_result = self.guardrails.check_question_fairness(question, topic)
        
        # Generate explanation
        explanation = self.explainability.explain_question_choice(thought_chain, context)
        
        # Log decision
        decision_id = self.accountability.log_decision(
            action_type="question_generation",
            input_data={"topic": topic, "context": context},
            output_data={"question": question},
            reasoning=thought_chain,
            safety_result=safety_result,
            explanation=explanation
        )
        
        return {
            "approved": safety_result.passed,
            "safety": {
                "level": safety_result.safety_level.value,
                "issues": safety_result.issues,
                "recommendations": safety_result.recommendations
            },
            "explanation": explanation,
            "decision_id": decision_id
        }
    
    def validate_and_explain_evaluation(self, evaluation: Dict[str, Any],
                                        answer: str, question: str,
                                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate evaluation and provide explanation"""
        # Check fairness
        fairness_result = self.guardrails.check_evaluation_fairness(evaluation, context)
        
        # Generate explanation
        explanation = self.explainability.explain_evaluation(evaluation, answer, question)
        
        # Log decision
        decision_id = self.accountability.log_decision(
            action_type="answer_evaluation",
            input_data={"question": question, "answer": answer[:100]},
            output_data=evaluation,
            reasoning={"confidence": evaluation.get("confidence", 0.7)},
            safety_result=fairness_result,
            explanation=explanation
        )
        
        return {
            "fair": fairness_result.passed,
            "fairness": {
                "level": fairness_result.safety_level.value,
                "issues": fairness_result.issues,
                "recommendations": fairness_result.recommendations
            },
            "explanation": explanation,
            "decision_id": decision_id
        }
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate any content for safety"""
        result = self.guardrails.check_content_safety(content)
        return {
            "safe": result.passed,
            "level": result.safety_level.value,
            "issues": result.issues,
            "explanation": result.explanation
        }
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status"""
        return {
            "audit_summary": self.accountability.get_audit_summary(),
            "compliance_report": self.accountability.generate_compliance_report()
        }
