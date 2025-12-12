"""
Autonomous Reasoning Engine for AI Interviewer
Self-Thinking, Logical Reasoning, and Self-Resilient System

This module implements MAANG-level autonomous AI capabilities:
- Chain-of-Thought (CoT) reasoning
- Self-reflection and meta-cognition
- Adaptive decision-making
- Self-healing and resilience
- Human-like interview conduct
"""

import logging
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..utils.config import Config
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate


from ..modules.learning_service import ReasoningBank
from .metacognitive import MetacognitiveSystem
from ..modules.critic_service import ReflectAgent

logger = logging.getLogger(__name__)



class ReasoningMode(Enum):
    """Reasoning modes for different contexts"""
    ANALYTICAL = "analytical"  # Deep analysis, logical breakdown
    EMPATHETIC = "empathetic"  # Understanding candidate state
    ADAPTIVE = "adaptive"      # Dynamic adjustment
    REFLECTIVE = "reflective"  # Self-evaluation
    STRATEGIC = "strategic"    # Long-term planning


class CandidateState(Enum):
    """Detected candidate states"""
    CONFIDENT = "confident"
    NERVOUS = "nervous"
    STRUGGLING = "struggling"
    EXCELLING = "excelling"
    NEUTRAL = "neutral"
    IMPROVING = "improving"
    DECLINING = "declining"


@dataclass
class ThoughtChain:
    """Represents a chain of thoughts during reasoning"""
    reasoning_id: str
    mode: ReasoningMode
    thoughts: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InterviewContext:
    """Rich context for autonomous decision-making"""
    session_id: str
    candidate_name: str
    topic: str
    question_number: int
    max_questions: int
    performance_history: List[float] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    candidate_state: CandidateState = CandidateState.NEUTRAL
    conversation_flow: List[Dict[str, Any]] = field(default_factory=list)
    emotional_cues: List[str] = field(default_factory=list)
    time_spent_per_question: List[float] = field(default_factory=list)


class AutonomousReasoningEngine:
    """
    Self-Thinking, Logical Reasoning Engine
    
    Implements human-like interview capabilities through:
    1. Chain-of-Thought (CoT) reasoning before actions
    2. Self-reflection on interview quality
    3. Adaptive behavior based on candidate state
    4. Self-healing error recovery
    5. Contextual memory and learning
    """
    
    def __init__(self, model_name: str = None, max_retries: int = 3):
        if model_name is None:
            model_name = Config.DEFAULT_MODEL
        self.model_name = model_name
        self.max_retries = max_retries
        self.thought_history: deque = deque(maxlen=100)
        self.self_reflection_cache: Dict[str, Any] = {}
        self.decision_log: List[Dict[str, Any]] = []
        self._llm = None
        self._current_model = None  # Tracks which model in fallback chain is active
        self._lock = threading.Lock()
        
        # Performance tracking for self-improvement
        self.performance_metrics = {
            "successful_reasonings": 0,
            "failed_reasonings": 0,
            "avg_reasoning_time": 0.0,
            "recovery_count": 0,
            "adaptation_count": 0
        }
        
        # Hybrid Research Modules (Safe Integration)
        self.reasoning_bank = None
        self.metacognitive = None
        
        try:
            self.reasoning_bank = ReasoningBank()
            self.metacognitive = MetacognitiveSystem()
            logger.info("✅ Hybrid modules loaded (ReasoningBank, Metacognitive)")
        except Exception as e:
            logger.warning(f"⚠️ Hybrid modules failed to load (running in standard mode): {e}")

        # Initialize with lazy loading
        logger.info("🧠 Autonomous Reasoning Engine initialized")
    
    def _get_llm(self) -> HuggingFaceEndpoint:
        """Lazy load Cloud LLM with intelligent fallback chain"""
        if self._llm is None:
            token = os.environ.get("HF_TOKEN")
            if not token:
                logger.warning("⚠️ HF_TOKEN not found! Falling back to public endpoints (may be rate limited).")
            
            # Try each model in the fallback chain
            for model_id in Config.MODEL_FALLBACK_CHAIN:
                try:
                    logger.info(f"🔄 Attempting to connect to: {model_id}")
                    llm = HuggingFaceEndpoint(
                        repo_id=model_id,
                        task="text-generation",
                        max_new_tokens=512,
                        top_k=50,
                        temperature=0.3,
                        huggingfacehub_api_token=token
                    )
                    # Test connection with a simple prompt
                    test_response = llm.invoke("Say 'ok' if you're working.")
                    if test_response:
                        self._llm = llm
                        self._current_model = model_id
                        logger.info(f"☁️ Connected to: {model_id}")
                        return self._llm
                except Exception as e:
                    error_str = str(e).lower()
                    if "rate" in error_str or "limit" in error_str or "429" in error_str:
                        logger.warning(f"⚠️ Rate limited on {model_id}, trying next...")
                    elif "503" in error_str or "unavailable" in error_str:
                        logger.warning(f"⚠️ Model {model_id} unavailable, trying next...")
                    else:
                        logger.warning(f"⚠️ Error with {model_id}: {e}")
                    import time
                    time.sleep(Config.MODEL_RETRY_DELAY)
                    continue
            
            logger.error("❌ All models in fallback chain failed!")
            self._llm = None
        return self._llm
    
    # ==================== CHAIN-OF-THOUGHT REASONING ====================
    
    def think_before_acting(self, context: InterviewContext, 
                           action_type: str) -> ThoughtChain:
        """
        Chain-of-Thought reasoning before any action
        
        This is the core of autonomous decision-making:
        1. Analyze current situation
        2. Consider multiple approaches
        3. Evaluate trade-offs
        4. Make reasoned decision
        """
        reasoning_id = hashlib.md5(
            f"{context.session_id}_{action_type}_{time.time()}".encode()
        ).hexdigest()[:12]
        
        thought_chain = ThoughtChain(
            reasoning_id=reasoning_id,
            mode=self._determine_reasoning_mode(context, action_type)
        )
        
        try:
            # Step 0: Hybrid Memory Retrieval (Safe Mode)
            memory_context = ""
            if self.reasoning_bank:
                try:
                    memories = self.reasoning_bank.retrieve(
                        context=f"{action_type} for {context.topic}",
                        topic=context.topic
                    )
                    memory_context = self.reasoning_bank.format_for_prompt(memories)
                except Exception as me:
                    logger.debug(f"Memory retrieval skip: {me}")

            # Step 1: Situational Analysis
            situation_analysis = self._analyze_situation(context)
            thought_chain.thoughts.append({
                "step": "situation_analysis",
                "thought": situation_analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 2: Consider Options
            options = self._generate_options(context, action_type, situation_analysis)
            thought_chain.thoughts.append({
                "step": "options_generation",
                "thought": f"Generated {len(options)} possible approaches",
                "options": options,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 3: Evaluate Trade-offs
            evaluation = self._evaluate_options(options, context)
            thought_chain.thoughts.append({
                "step": "trade_off_evaluation",
                "thought": evaluation,
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 4: Make Decision
            decision = self._make_reasoned_decision(options, evaluation, context)
            thought_chain.conclusion = decision["chosen_approach"]
            thought_chain.confidence = decision["confidence"]
            thought_chain.metadata = decision["reasoning"]
            
            # Log successful reasoning
            self.performance_metrics["successful_reasonings"] += 1
            self.thought_history.append(thought_chain)
            
        except Exception as e:
            logger.error(f"❌ Reasoning failed: {e}")
            thought_chain.conclusion = self._get_safe_fallback(action_type)
            thought_chain.confidence = 0.3
            self.performance_metrics["failed_reasonings"] += 1
        
        return thought_chain
    
    def _analyze_situation(self, context: InterviewContext) -> Dict[str, Any]:
        """Analyze current interview situation"""
        analysis = {
            "interview_progress": f"{context.question_number}/{context.max_questions}",
            "performance_trend": self._calculate_trend(context.performance_history),
            "candidate_state": context.candidate_state.value,
            "knowledge_profile": {
                "gaps": context.knowledge_gaps[:3] if context.knowledge_gaps else [],
                "strengths": context.strengths[:3] if context.strengths else []
            },
            "emotional_state": self._interpret_emotional_cues(context.emotional_cues),
            "time_pressure": self._assess_time_pressure(context)
        }
        return analysis
    
    def _determine_reasoning_mode(self, context: InterviewContext, 
                                  action_type: str) -> ReasoningMode:
        """Determine appropriate reasoning mode based on context"""
        if context.candidate_state in [CandidateState.NERVOUS, CandidateState.STRUGGLING]:
            return ReasoningMode.EMPATHETIC
        elif context.candidate_state == CandidateState.EXCELLING:
            return ReasoningMode.STRATEGIC
        elif action_type == "evaluate":
            return ReasoningMode.ANALYTICAL
        elif action_type == "self_check":
            return ReasoningMode.REFLECTIVE
        else:
            return ReasoningMode.ADAPTIVE
    
    def _generate_options(self, context: InterviewContext, action_type: str,
                         situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate possible approaches based on situation"""
        options = []
        
        if action_type == "generate_question":
            # Different questioning strategies
            options.extend([
                {
                    "approach": "progressive_challenge",
                    "description": "Gradually increase difficulty based on performance",
                    "suitability": 0.7 if situation["performance_trend"] == "improving" else 0.3
                },
                {
                    "approach": "gap_focused",
                    "description": "Target identified knowledge gaps",
                    "suitability": 0.8 if situation["knowledge_profile"]["gaps"] else 0.2
                },
                {
                    "approach": "strength_building",
                    "description": "Build on demonstrated strengths",
                    "suitability": 0.6 if situation.get("candidate_state") == "nervous" else 0.4
                },
                {
                    "approach": "exploratory",
                    "description": "Explore new areas to discover hidden competencies",
                    "suitability": 0.5
                }
            ])
        
        elif action_type == "evaluate":
            options.extend([
                {
                    "approach": "comprehensive",
                    "description": "Full multi-dimensional evaluation",
                    "suitability": 0.8
                },
                {
                    "approach": "focused",
                    "description": "Focus on key technical aspects",
                    "suitability": 0.6
                },
                {
                    "approach": "encouraging",
                    "description": "Emphasize positives while noting improvements",
                    "suitability": 0.7 if situation["candidate_state"] == "nervous" else 0.4
                }
            ])
        
        return options
    
    def _evaluate_options(self, options: List[Dict[str, Any]], 
                         context: InterviewContext) -> Dict[str, Any]:
        """Evaluate trade-offs between options"""
        evaluations = []
        
        for option in options:
            evaluation = {
                "approach": option["approach"],
                "pros": self._identify_pros(option, context),
                "cons": self._identify_cons(option, context),
                "risk_level": self._assess_risk(option, context),
                "expected_outcome": self._predict_outcome(option, context),
                "adjusted_score": option["suitability"]
            }
            
            # Adjust score based on candidate state
            if context.candidate_state == CandidateState.STRUGGLING:
                if option["approach"] in ["strength_building", "encouraging"]:
                    evaluation["adjusted_score"] += 0.2
            
            evaluations.append(evaluation)
        
        # Guard against empty evaluations list
        if not evaluations:
            return {
                "evaluations": [],
                "recommendation": {"approach": "exploratory", "adjusted_score": 0.5, "pros": [], "cons": []}
            }
        
        return {
            "evaluations": evaluations,
            "recommendation": max(evaluations, key=lambda x: x["adjusted_score"])
        }
    
    def _make_reasoned_decision(self, options: List[Dict[str, Any]],
                               evaluation: Dict[str, Any],
                               context: InterviewContext) -> Dict[str, Any]:
        """Make final decision with reasoning"""
        best_option = evaluation["recommendation"]
        
        return {
            "chosen_approach": best_option["approach"],
            "confidence": min(best_option["adjusted_score"], 0.95),
            "reasoning": {
                "primary_factor": f"Best fit for {context.candidate_state.value} candidate",
                "supporting_evidence": best_option["pros"],
                "risks_acknowledged": best_option["cons"],
                "fallback_plan": self._identify_fallback(options, best_option)
            }
        }
    
    # ==================== SELF-REFLECTION ====================
    
    def self_reflect(self, recent_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Self-reflection on interview quality
        
        Meta-cognition: Thinking about how we're thinking
        """
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "actions_reviewed": len(recent_actions),
            "insights": [],
            "improvements": [],
            "confidence_in_approach": 0.0
        }
        
        try:
            # Analyze recent action quality
            action_quality = self._assess_action_quality(recent_actions)
            reflection["action_quality"] = action_quality
            
            # Identify patterns
            patterns = self._identify_patterns(recent_actions)
            reflection["patterns"] = patterns
            
            # Generate self-improvement suggestions
            suggestions = self._generate_improvement_suggestions(action_quality, patterns)
            reflection["improvements"] = suggestions
            
            # Calculate confidence
            reflection["confidence_in_approach"] = self._calculate_self_confidence(
                action_quality, patterns
            )
            
            # Insights from reflection
            if action_quality["average_score"] < 0.6:
                reflection["insights"].append(
                    "Performance below target - consider adjusting approach"
                )
            if patterns.get("candidate_struggling"):
                reflection["insights"].append(
                    "Candidate showing signs of difficulty - increase support"
                )
            
            self.self_reflection_cache[datetime.now().isoformat()] = reflection
            
        except Exception as e:
            logger.error(f"Self-reflection error: {e}")
            reflection["error"] = str(e)
        
        return reflection
    
    def _assess_action_quality(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess quality of recent actions"""
        if not actions:
            return {"average_score": 0.5, "variance": 0.0}
        
        scores = [a.get("score", 0.5) for a in actions]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        return {
            "average_score": avg_score,
            "variance": self._calculate_variance(scores),
            "trend": self._calculate_trend(scores),
            "best_action": max(actions, key=lambda x: x.get("score", 0)) if actions else {},
            "worst_action": min(actions, key=lambda x: x.get("score", 0)) if actions else {}
        }
    
    def _identify_patterns(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify patterns in recent actions"""
        patterns = {
            "candidate_struggling": False,
            "interview_flowing": True,
            "repetitive_questions": False,
            "improvement_observed": False
        }
        
        if len(actions) >= 3:
            recent_scores = [a.get("score", 0.5) for a in actions[-3:]]
            if all(s < 0.5 for s in recent_scores):
                patterns["candidate_struggling"] = True
            if self._calculate_trend(recent_scores) == "improving":
                patterns["improvement_observed"] = True
        
        return patterns
    
    def _generate_improvement_suggestions(self, quality: Dict[str, Any],
                                         patterns: Dict[str, Any]) -> List[str]:
        """Generate self-improvement suggestions"""
        suggestions = []
        
        if quality["average_score"] < 0.5:
            suggestions.append("Consider simplifying questions")
        if patterns.get("candidate_struggling"):
            suggestions.append("Provide more encouraging feedback")
            suggestions.append("Offer hints or partial answers")
        if quality.get("variance", 0) > 0.3:
            suggestions.append("Aim for more consistent question difficulty")
        
        return suggestions
    
    # ==================== RESUME ANALYSIS ====================
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze resume to extract skills, experience, and key qualifications.
        Used for personalized interview questions.
        """
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                "skills": [],
                "experience_years": 0,
                "key_qualifications": [],
                "suggested_topics": [],
                "analysis_type": "empty"
            }
        
        try:
            llm = self._get_llm()
            if llm:
                prompt = f"""[INST] Analyze this resume and extract key information.

RESUME:
{resume_text[:3000]}

Return JSON only:
{{"skills": ["skill1", "skill2"], "experience_years": <number>, "key_qualifications": ["qual1"], "suggested_topics": ["topic1"], "summary": "brief summary"}}
[/INST]"""
                
                response = llm.invoke(prompt)
                
                import json
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    result = json.loads(response[start:end])
                    result["analysis_type"] = "llm"
                    return result
        except Exception as e:
            logger.warning(f"Resume LLM analysis failed: {e}")
        
        # Heuristic fallback
        skills = []
        text_lower = resume_text.lower()
        
        skill_keywords = {
            "python": "Python", "javascript": "JavaScript", "java": "Java",
            "react": "React", "node": "Node.js", "sql": "SQL",
            "aws": "AWS", "docker": "Docker", "kubernetes": "Kubernetes",
            "machine learning": "Machine Learning", "data science": "Data Science",
            "api": "API Development", "agile": "Agile", "scrum": "Scrum"
        }
        
        for kw, skill in skill_keywords.items():
            if kw in text_lower:
                skills.append(skill)
        
        return {
            "skills": skills[:10],
            "experience_years": self._estimate_experience(resume_text),
            "key_qualifications": skills[:3],
            "suggested_topics": self._suggest_topics(skills),
            "analysis_type": "heuristic"
        }
    
    def _estimate_experience(self, text: str) -> int:
        """Estimate years of experience from resume text."""
        import re
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience[:\s]+(\d+)\s*years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return min(int(match.group(1)), 30)
        return 0
    
    def _suggest_topics(self, skills: list) -> list:
        """Suggest interview topics based on skills."""
        topic_map = {
            "Python": "Python/Backend Development",
            "JavaScript": "JavaScript/Frontend Development",
            "React": "JavaScript/Frontend Development",
            "AWS": "Cloud & DevOps (AWS/GCP/Azure)",
            "Docker": "Cloud & DevOps (AWS/GCP/Azure)",
            "SQL": "Database & SQL",
            "Machine Learning": "Machine Learning/AI",
            "API Development": "API Design & REST"
        }
        topics = set()
        for skill in skills:
            if skill in topic_map:
                topics.add(topic_map[skill])
        return list(topics)[:3] if topics else ["Python/Backend Development"]
    
    # ==================== HUMAN-LIKE INTERVIEW CONDUCT ====================
    
    def generate_human_like_question(self, context: InterviewContext,
                                     thought_chain: ThoughtChain) -> Dict[str, Any]:
        """
        Generate question with human interviewer characteristics:
        - Natural conversation flow
        - Contextual references to previous answers
        - Empathetic adaptation
        - Professional but warm tone
        """
        # Think before generating
        if thought_chain.conclusion is None:
            thought_chain = self.think_before_acting(context, "generate_question")
        
        approach = thought_chain.conclusion or "progressive_challenge"
        
        # Build human-like question with reasoning
        question_data = self._build_contextual_question(context, approach)
        
        # Add human touches
        question_data["human_elements"] = {
            "acknowledgment": self._generate_acknowledgment(context),
            "transition": self._generate_natural_transition(context),
            "encouragement": self._generate_encouragement(context) if context.candidate_state == CandidateState.STRUGGLING else None
        }
        
        # Compose final question
        final_question = self._compose_human_question(question_data)
        
        return {
            "question": final_question,
            "metadata": {
                "approach": approach,
                "reasoning_id": thought_chain.reasoning_id,
                "confidence": thought_chain.confidence,
                "human_elements": question_data["human_elements"]
            }
        }
    
    def _build_contextual_question(self, context: InterviewContext,
                                   approach: str) -> Dict[str, Any]:
        """Build question with full context awareness"""
        # Use progressive questions based on question number (avoid repetition!)
        question = self.get_progressive_question(
            context.topic, 
            context.question_number + 1,  # Next question number
            approach
        )
        
        # Determine difficulty based on performance
        difficulty = self._calculate_adaptive_difficulty(context)
        
        return {
            "template": question,
            "focus_area": context.topic,
            "difficulty": difficulty,
            "context_reference": self._get_context_reference(context)
        }
    
    def _generate_acknowledgment(self, context: InterviewContext) -> Optional[str]:
        """Generate acknowledgment of previous answer"""
        if not context.conversation_flow:
            return None
        
        last_score = context.performance_history[-1] if context.performance_history else 5
        
        acknowledgments = {
            "high": [
                "That's an excellent point.",
                "Great explanation!",
                "You've clearly understood this well."
            ],
            "medium": [
                "Good thinking.",
                "That covers the basics well.",
                "I see your approach."
            ],
            "low": [
                "Thanks for sharing your thoughts.",
                "I appreciate the attempt.",
                "Let me build on that."
            ]
        }
        
        if last_score >= 8:
            category = "high"
        elif last_score >= 5:
            category = "medium"
        else:
            category = "low"
        
        import random
        return random.choice(acknowledgments[category])
    
    def _generate_natural_transition(self, context: InterviewContext) -> str:
        """Generate natural transition to next question"""
        import random
        
        transitions = [
            "Moving on,",
            "Let's explore another area.",
            "Building on that,",
            "Now I'd like to ask about",
            "Here's something related:",
            "Let's dive deeper.",
            "Next up,",
            "Continuing our discussion,"
        ]
        
        excelling_transitions = [
            "Since you're doing well, let's try something challenging:",
            "Great progress! Here's a tougher one:",
            "You're on fire! Let me push you a bit:",
            "Impressive so far! Let's go deeper:",
            "Building on your strong answer,"
        ]
        
        # Context-aware selection
        if context.question_number == 1:
            return "Let's start with"
        elif context.question_number == context.max_questions:
            return "For our final question,"
        elif context.candidate_state == CandidateState.EXCELLING:
            return random.choice(excelling_transitions)
        elif context.candidate_state == CandidateState.STRUGGLING:
            return "Let's try a different angle:"
        else:
            return random.choice(transitions)
    
    def _generate_encouragement(self, context: InterviewContext) -> str:
        """Generate encouraging words for struggling candidates"""
        encouragements = [
            "Don't worry if you're not sure - just share your thinking.",
            "Take your time with this one.",
            "There's no wrong answer - I'm interested in your approach.",
            "Feel free to think out loud.",
            "Let's work through this together."
        ]
        import random
        return random.choice(encouragements)
    
    def _compose_human_question(self, question_data: Dict[str, Any]) -> str:
        """Compose final human-like question"""
        parts = []
        
        elements = question_data.get("human_elements", {})
        
        # Add acknowledgment if present
        if elements.get("acknowledgment"):
            parts.append(elements["acknowledgment"])
        
        # Add encouragement if struggling
        if elements.get("encouragement"):
            parts.append(elements["encouragement"])
        
        # Add transition
        if elements.get("transition"):
            parts.append(elements["transition"])
        
        # Add main question
        parts.append(question_data.get("template", "Tell me about your experience."))
        
        return " ".join(parts)
    
    # ==================== SELF-RESILIENCE ====================
    
    def recover_from_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Self-healing: Recover gracefully from errors
        """
        logger.warning(f"⚠️ Error recovery initiated: {error}")
        self.performance_metrics["recovery_count"] += 1
        
        recovery_response = {
            "status": "recovered",
            "original_error": str(error),
            "recovery_action": None,
            "fallback_used": True
        }
        
        error_type = type(error).__name__
        
        # Strategy based on error type
        if "Connection" in error_type or "Timeout" in error_type:
            recovery_response["recovery_action"] = "llm_reconnect"
            self._llm = None  # Force reconnection
            self._get_llm()  # Attempt reconnect
            
        elif "JSON" in error_type:
            recovery_response["recovery_action"] = "parse_fallback"
            # Use regex or simpler parsing
            
        elif "Value" in error_type:
            recovery_response["recovery_action"] = "default_values"
            
        else:
            recovery_response["recovery_action"] = "graceful_degradation"
        
        return recovery_response
    
    def adapt_to_situation(self, context: InterviewContext) -> Dict[str, Any]:
        """
        Adaptive behavior based on real-time signals
        """
        self.performance_metrics["adaptation_count"] += 1
        
        adaptations = {
            "difficulty_adjustment": 0,
            "tone_adjustment": "neutral",
            "pace_adjustment": "normal",
            "support_level": "standard"
        }
        
        # Analyze candidate state
        if context.candidate_state == CandidateState.STRUGGLING:
            adaptations["difficulty_adjustment"] = -1
            adaptations["tone_adjustment"] = "encouraging"
            adaptations["support_level"] = "high"
            
        elif context.candidate_state == CandidateState.EXCELLING:
            adaptations["difficulty_adjustment"] = +1
            adaptations["tone_adjustment"] = "challenging"
            adaptations["support_level"] = "minimal"
            
        elif context.candidate_state == CandidateState.NERVOUS:
            adaptations["pace_adjustment"] = "slower"
            adaptations["tone_adjustment"] = "warm"
            adaptations["support_level"] = "high"
        
        return adaptations
    
    # ==================== HELPER METHODS ====================
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"
        
        recent = values[-3:] if len(values) >= 3 else values
        if recent[-1] > recent[0] + 0.5:
            return "improving"
        elif recent[-1] < recent[0] - 0.5:
            return "declining"
        return "stable"
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _calculate_self_confidence(self, quality: Dict[str, Any],
                                   patterns: Dict[str, Any]) -> float:
        """Calculate confidence in current approach"""
        base_confidence = quality.get("average_score", 0.5)
        
        if patterns.get("improvement_observed"):
            base_confidence += 0.1
        if patterns.get("candidate_struggling"):
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def _interpret_emotional_cues(self, cues: List[str]) -> str:
        """Interpret emotional cues from conversation"""
        if not cues:
            return "neutral"
        
        positive_words = ["confident", "clear", "good", "understand"]
        negative_words = ["unsure", "confused", "difficult", "nervous"]
        
        positive_count = sum(1 for cue in cues if any(p in cue.lower() for p in positive_words))
        negative_count = sum(1 for cue in cues if any(n in cue.lower() for n in negative_words))
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "anxious"
        return "neutral"
    
    def _assess_time_pressure(self, context: InterviewContext) -> str:
        """Assess time pressure based on context"""
        progress = context.question_number / context.max_questions
        
        if progress > 0.8:
            return "high"
        elif progress > 0.5:
            return "moderate"
        return "low"
    
    def _identify_pros(self, option: Dict[str, Any], 
                      context: InterviewContext) -> List[str]:
        """Identify pros of an option"""
        pros = []
        if option["suitability"] > 0.6:
            pros.append("High suitability for current context")
        if option["approach"] == "gap_focused" and context.knowledge_gaps:
            pros.append("Addresses known gaps")
        if option["approach"] == "encouraging" and context.candidate_state == CandidateState.STRUGGLING:
            pros.append("Matches candidate's emotional needs")
        return pros or ["Standard approach"]
    
    def _identify_cons(self, option: Dict[str, Any],
                      context: InterviewContext) -> List[str]:
        """Identify cons of an option"""
        cons = []
        if option["suitability"] < 0.4:
            cons.append("Low suitability score")
        if option["approach"] == "progressive_challenge" and context.candidate_state == CandidateState.STRUGGLING:
            cons.append("May overwhelm struggling candidate")
        return cons or ["No significant drawbacks"]
    
    def _assess_risk(self, option: Dict[str, Any],
                    context: InterviewContext) -> str:
        """Assess risk level of an option"""
        risk_score = 0
        
        if option["suitability"] < 0.4:
            risk_score += 2
        if context.candidate_state == CandidateState.STRUGGLING:
            risk_score += 1
        
        if risk_score >= 2:
            return "high"
        elif risk_score >= 1:
            return "medium"
        return "low"
    
    def _predict_outcome(self, option: Dict[str, Any],
                        context: InterviewContext) -> str:
        """Predict likely outcome of option"""
        if option["suitability"] > 0.7:
            return "likely_positive"
        elif option["suitability"] > 0.4:
            return "uncertain"
        return "likely_negative"
    
    def _identify_fallback(self, options: List[Dict[str, Any]],
                          chosen: Dict[str, Any]) -> str:
        """Identify fallback if chosen approach fails"""
        other_options = [o for o in options if o["approach"] != chosen["approach"]]
        if other_options:
            return max(other_options, key=lambda x: x.get("suitability", 0))["approach"]
        return "default_approach"

    # ==================== REFLEXION CAPABILITIES (Phase 4) ====================

    def critique_draft(self, draft: str, context: InterviewContext, task: str = "question") -> Dict[str, Any]:
        """
        Critique a draft outputs against quality standards.
        Used by Reflexion Loop.
        """
        try:
            llm = self._get_llm()
            if not llm:
                return {"score": 8, "feedback": "Self-Critique unavailable (No LLM)."} # Pass by default

            prompt = f"""You are a Senior Technical Interviewer mentoring a junior interviewer.
            
            CRITIQUE TASK: Evaluate this proposed interview {task} for quality, clarity, and relevance.
            
            CONTEXT:
            Topic: {context.topic}
            Candidate State: {context.candidate_state.value}
            Trend: {self._calculate_trend(context.performance_history)}
            
            DRAFT {task.upper()}:
            "{draft}"
            
            CRITERIA:
            1. Is it clear and concise? (No ambiguity)
            2. Is the difficulty appropriate? (Adapts to candidate state)
            3. Is it relevant to the topic?
            4. Is the tone professional yet encouraging?
            
            OUTPUT JSON ONLY:
            {{
                "score": <0-10>,
                "reasoning": "brief explanation",
                "suggestions": ["suggestion 1", "..."]
            }}
            """
            
            response = llm.invoke(prompt)
            
            # Simple JSON extraction
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            
            return {"score": 7, "feedback": "Failed to parse critique."}

        except Exception as e:
            logger.warning(f"Critique failed: {e}")
            return {"score": 8, "feedback": "Critique error fallback."}

    def revise_draft(self, draft: str, critique: Dict[str, Any], context: InterviewContext) -> str:
        """
        Revise a draft based on critique feedback.
        """
        try:
            llm = self._get_llm()
            if not llm:
                return draft 

            prompt = f"""You are an Expert Technical Interviewer.
            
            TASK: Revise this draft interview question based on the critique.
            
            DRAFT: "{draft}"
            
            CRITIQUE:
            Score: {critique.get('score')}
            Feedback: {critique.get('reasoning')}
            Suggestions: {critique.get('suggestions')}
            
            Generate ONLY the revised text. Do not add quotes or explanations.
            """
            
            revised = llm.invoke(prompt).strip()
            # Remove quotes if present
            if revised.startswith('"') and revised.endswith('"'):
                revised = revised[1:-1]
            return revised

        except Exception as e:
            logger.warning(f"Revision failed: {e}")
            return draft
    
    
    def decide_transition(self, context: InterviewContext) -> Dict[str, Any]:
        """
        Decide interview phase transition based on candidate state.
        Includes PRIVACY GUARDRAILS: Internal state is detailed, external is sanitized.
        """
        try:
            llm = self._get_llm()
            
            # 1. Analyze Situation (Internal)
            analysis = self._analyze_situation(context)
            
            # 2. Heuristic Check (Guardrail Base)
            # If candidate is struggling badly, DO NOT advance to Deep Dive regardless of what LLM says.
            heuristic_decision = "stay"
            if context.candidate_state == CandidateState.STRUGGLING and context.question_number < context.max_questions:
                 heuristic_decision = "switch_to_support"
            elif context.candidate_state == CandidateState.EXCELLING:
                 heuristic_decision = "advance"
                 
            # 3. LLM Decision (Refinement)
            if llm:
                prompt = f"""
                You are an Expert Interview Conductor.
                
                CONTEXT:
                - Progress: {context.question_number}/{context.max_questions}
                - State: {context.candidate_state.value} (INTERNAL ONLY)
                - Trend: {analysis['performance_trend']}
                - Heuristic Recommendation: {heuristic_decision}
                
                DECISION:
                Should we:
                - "stay": Keep current difficulty/phase.
                - "advance": Increase challenge/move to next phase.
                - "support": Switch to easier/supportive mode.
                
                OUTPUT JSON:
                {{
                    "decision": "stay" | "advance" | "support",
                    "reasoning": "Brief reason...",
                    "ui_label": "Neutral label for UI (e.g. 'Standard', 'Focus', 'Challenge')" 
                }}
                """
                response = llm.invoke(prompt)
                import json
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    result = json.loads(response[start:end])
                else:
                    result = {"decision": heuristic_decision, "ui_label": "Standard Mode"}
            else:
                 result = {"decision": heuristic_decision, "ui_label": "Standard Mode"}

            # 4. Enforce Privacy Guardrail on UI Label
            # Ensure UI label never leaks "Struggling" or negative terms
            safe_labels = {
                "stay": "Standard Pace",
                "advance": "Challenge Mode",
                "support": "Supportive Pace"
            }
            final_ui_label = result.get("ui_label", safe_labels.get(result["decision"], "Standard"))
            
            # Double check against blacklist
            blacklist = ["struggling", "failing", "bad", "nervous"]
            if any(b in final_ui_label.lower() for b in blacklist):
                final_ui_label = safe_labels.get(result["decision"], "Standard")

            return {
                "decision": result["decision"],
                "ui_label": final_ui_label,
                "internal_state": context.candidate_state.value
            }

        except Exception as e:
            logger.error(f"Transition decision failed: {e}")
            return {"decision": "stay", "ui_label": "Standard Pace"}
    
    def _get_safe_fallback(self, action_type: str) -> str:
        """Get safe fallback for action type"""
        fallbacks = {
            "generate_question": "exploratory",
            "evaluate": "comprehensive",
            "decide": "adaptive"
        }
        return fallbacks.get(action_type, "default")
    
    def _calculate_adaptive_difficulty(self, context: InterviewContext) -> str:
        """Calculate adaptive difficulty level"""
        if not context.performance_history:
            return "medium"
        
        avg_score = sum(context.performance_history) / len(context.performance_history)
        
        if avg_score >= 8:
            return "hard"
        elif avg_score >= 5:
            return "medium"
        return "easy"
    
    def _get_context_reference(self, context: InterviewContext) -> Optional[str]:
        """Get reference to previous conversation for continuity"""
        if not context.conversation_flow:
            return None
        
        last_exchange = context.conversation_flow[-1]
        return last_exchange.get("topic_mentioned")
    
    def _get_question_templates(self, topic: str) -> Dict[str, str]:
        """Get question templates for topic"""
        templates = {
            "JavaScript/Frontend Development": {
                "default": "Can you explain how JavaScript handles asynchronous operations?",
                "gap_focused": "Let's explore closures. Can you explain how they work?",
                "strength_building": "You mentioned React earlier. Can you dive deeper into its component lifecycle?",
                "progressive_challenge": "How would you optimize a React application for performance?"
            },
            "Python/Backend Development": {
                "default": "How would you design a RESTful API in Python?",
                "gap_focused": "Can you explain Python's memory management?",
                "strength_building": "You seem comfortable with Django. How would you handle complex queries?",
                "progressive_challenge": "Explain how you'd implement a microservices architecture."
            }
        }
        return templates.get(topic, {
            "default": f"Tell me about your experience with {topic}.",
            "gap_focused": f"Can you explain a concept in {topic} that you find challenging?",
            "strength_building": f"What's a {topic} project you're proud of?",
            "progressive_challenge": f"Describe a complex {topic} problem you've solved."
        })
    
    def get_progressive_question(self, topic: str, question_number: int, 
                                  approach: str = "default") -> str:
        """Get a unique question based on question number to avoid repetition."""
        # Question banks by topic with 5 progressive questions each
        question_banks = {
            "Machine Learning/AI": [
                "Can you explain the difference between supervised and unsupervised learning?",
                "How do you handle overfitting in machine learning models?",
                "Explain the concept of gradient descent and its variants.",
                "How would you approach a classification problem with imbalanced data?",
                "What are transformers and why are they important in modern AI?"
            ],
            "Python/Backend Development": [
                "What are Python decorators and when would you use them?",
                "How do you handle database transactions in a Python application?",
                "Explain the difference between threads and async in Python.",
                "How would you design a scalable API rate limiting system?",
                "What strategies do you use for error handling in production code?"
            ],
            "JavaScript/Frontend Development": [
                "Explain how the event loop works in JavaScript.",
                "What are closures and how have you used them?",
                "How do you manage state in a complex React application?",
                "What strategies do you use for optimizing frontend performance?",
                "Explain the concept of virtual DOM and reconciliation."
            ],
            "System Design": [
                "How would you design a URL shortening service?",
                "Explain your approach to designing a distributed cache.",
                "How would you handle millions of concurrent users?",
                "What are the tradeoffs between SQL and NoSQL databases?",
                "How do you ensure data consistency in distributed systems?"
            ],
            "Data Structures & Algorithms": [
                "Explain the time complexity of common sorting algorithms.",
                "When would you use a hash table vs a binary search tree?",
                "How do you approach solving dynamic programming problems?",
                "Explain how a priority queue works internally.",
                "What graph algorithms are you familiar with?"
            ]
        }
        
        # Clean topic to avoid word repetition ("interview interview")
        topic_clean = topic
        if "interview" in topic.lower():
            topic_clean = topic.lower().replace(" interview", "").replace("interview ", "").strip()
            topic_clean = topic_clean.title() if topic_clean else "technical skills"
        
        # Default questions for unknown topics
        default_questions = [
            f"Tell me about your background in {topic_clean}.",
            f"What's the most challenging {topic_clean} problem you've solved?",
            f"How do you stay updated with developments in {topic_clean}?",
            f"Describe a recent project involving {topic_clean}.",
            f"What best practices do you follow when working with {topic_clean}?"
        ]
        
        questions = question_banks.get(topic, default_questions)
        
        # Get question based on number (0-indexed, wrap around)
        idx = (question_number - 1) % len(questions)
        return questions[idx]

    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for self-monitoring"""
        return {
            "metrics": self.performance_metrics,
            "thought_history_size": len(self.thought_history),
            "reflection_cache_size": len(self.self_reflection_cache),
            "decision_log_size": len(self.decision_log),
            "llm_status": "connected" if self._llm else "disconnected"
        }
