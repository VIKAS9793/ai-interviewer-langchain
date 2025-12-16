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
from typing import Dict, List, Any, Optional, Tuple, cast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..utils.config import Config
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import os
from langchain_huggingface import HuggingFaceEndpoint  # pyright: ignore[reportMissingImports]
from langchain_core.prompts import PromptTemplate


from ..modules.learning_service import ReasoningBank
from .metacognitive import MetacognitiveSystem
from ..modules.critic_service import ReflectAgent

# Pydantic for structured output (Architecture Audit P1)
try:
    from pydantic import BaseModel, Field, SecretStr
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None  # type: ignore[assignment, misc]
    SecretStr = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)


# ==================== PYDANTIC MODELS (P1: Structured Output) ====================

if PYDANTIC_AVAILABLE:
    class ResumeAnalysis(BaseModel):
        """Structured output for resume analysis - ensures type safety."""
        skills: list = Field(default_factory=list, description="Technical and soft skills extracted from resume")
        experience_years: int = Field(default=0, description="Total years of professional experience")
        key_qualifications: list = Field(default_factory=list, description="Key qualifications and certifications")
        suggested_topics: list = Field(default_factory=list, description="Suggested interview topics based on resume")
        summary: str = Field(default="", description="Brief summary of candidate profile")
else:
    ResumeAnalysis = None  # type: ignore[assignment, misc]



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
    company_name: Optional[str] = None
    previous_questions: List[str] = field(default_factory=list)


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
    
    def __init__(self, model_name: Optional[str] = None, max_retries: int = 3):
        if model_name is None:
            model_name = Config.DEFAULT_MODEL
        self.model_name = model_name
        self.max_retries = max_retries
        self.thought_history: deque = deque(maxlen=100)
        self.self_reflection_cache: Dict[str, Any] = {}
        self.decision_log: List[Dict[str, Any]] = []
        self._llm: Any = None
        self._current_model: Optional[str] = None  # Tracks which model in fallback chain is active
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
    
    def _get_llm(self):
        """
        Lazy load LLM with hybrid provider support (Arch Audit A+B).
        Priority based on Config.LLM_PROVIDER:
        - "gemini": Use Google Gemini only
        - "openai": Use OpenAI only
        - "huggingface": Use HuggingFace only
        - "hybrid": Try Gemini -> OpenAI -> HuggingFace
        
        Rate Limiting: Checks quota before Gemini, auto-fallback if exhausted.
        """
        if self._llm is None:
            provider = Config.LLM_PROVIDER
            
            # RATE LIMITER CHECK: Prevent Gemini if quota exhausted
            from src.ai_interviewer.utils.rate_limiter import get_rate_limiter
            rate_limiter = get_rate_limiter()
            
            # Try Gemini first if hybrid or gemini mode
            if provider in ("gemini", "hybrid"):
                # Check if we have quota remaining
                if rate_limiter.daily_quota.is_quota_exhausted():
                    logger.warning("⚠️ Gemini quota exhausted (20 RPD), skipping to fallback")
                    if provider == "gemini":
                        raise Exception("Gemini quota exhausted and no fallback configured")
                    # Skip to OpenAI/HuggingFace
                else:
                    try:
                        gemini_key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
                        if gemini_key:
                            from langchain_google_genai import ChatGoogleGenerativeAI  # pyright: ignore[reportMissingImports]
                            self._llm = ChatGoogleGenerativeAI(
                                model=Config.GEMINI_MODEL,
                                temperature=Config.GEMINI_TEMPERATURE,
                                google_api_key=gemini_key
                            )
                            self._current_model = f"gemini/{Config.GEMINI_MODEL}"
                            # Record the request for quota tracking
                            rate_limiter.daily_quota.record_request()
                            logger.info(f"✅ Connected to Gemini: {Config.GEMINI_MODEL} ({rate_limiter.daily_quota.requests_today}/{Config.RATE_LIMIT_RPD} RPD used)")
                            return self._llm
                        elif provider == "gemini":
                            logger.warning("⚠️ GEMINI_API_KEY not found but LLM_PROVIDER=gemini")
                    except Exception as e:
                        error_str = str(e).lower()
                        # Detect 429 quota errors
                        if "429" in error_str or "quota" in error_str or "resourceexhausted" in error_str:
                            logger.warning(f"⚠️ Gemini quota exhausted (429): {e}")
                            # Mark quota as exhausted to prevent further attempts
                            rate_limiter.daily_quota._requests_today = Config.RATE_LIMIT_RPD
                            if provider == "gemini":
                                raise  # No fallback available
                            # Fall through to try OpenAI/HuggingFace
                        else:
                            logger.warning(f"⚠️ Gemini connection failed: {e}")
                            if provider == "gemini":
                                raise  # Don't fallback if explicitly set to gemini
            
            # Try OpenAI if hybrid or openai mode
            if provider in ("openai", "hybrid"):
                try:
                    openai_key = os.environ.get("OPENAI_API_KEY")
                    if openai_key:
                        from langchain_openai import ChatOpenAI  # pyright: ignore[reportMissingImports]
                        # Convert str to SecretStr for type safety
                        api_key_secret: Any
                        if PYDANTIC_AVAILABLE and SecretStr is not None:
                            api_key_secret = SecretStr(openai_key)
                        else:
                            api_key_secret = openai_key
                        self._llm = ChatOpenAI(
                            model=Config.OPENAI_MODEL,
                            temperature=Config.OPENAI_TEMPERATURE,
                            api_key=api_key_secret
                        )
                        self._current_model = f"openai/{Config.OPENAI_MODEL}"
                        logger.info(f"✅ Connected to OpenAI: {Config.OPENAI_MODEL}")
                        return self._llm
                    elif provider == "openai":
                        logger.warning("⚠️ OPENAI_API_KEY not found but LLM_PROVIDER=openai")
                except Exception as e:
                    logger.warning(f"⚠️ OpenAI connection failed: {e}")
                    if provider == "openai":
                        raise  # Don't fallback if explicitly set to openai
            
            # Fallback to HuggingFace
            token = os.environ.get("HF_TOKEN")
            if not token:
                logger.warning("⚠️ HF_TOKEN not found! Falling back to public endpoints.")
            
            # Try each model in the fallback chain
            for model_id in Config.MODEL_FALLBACK_CHAIN:
                try:
                    logger.info(f"🔄 Attempting to connect to: {model_id}")
                    llm = HuggingFaceEndpoint(
                        repo_id=model_id,
                        model=model_id,  # Some versions require both repo_id and model
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
    
    def invoke_with_quota_check(self, *args, **kwargs):
        """
        CRITICAL FIX: Invoke wrapper that checks quota BEFORE every call.
        
        This solves the caching bug where self._llm bypasses quota checks.
        Every LLM.invoke() in this file should use this method instead.
        
        Behavior:
        1. Check if Gemini quota exhausted BEFORE invoke
        2. If exhausted, switch to fallback immediately
        3. If invoke raises 429, mark quota exhausted and retry with fallback
        4. Track all Gemini requests for quota management
        
        Returns:
            AIMessage from LLM
        """
        from src.ai_interviewer.utils.rate_limiter import get_rate_limiter
        rate_limiter = get_rate_limiter()
        
        # Check if currently using Gemini
        is_using_gemini = "gemini" in (self._current_model or "").lower()
        
        # PRE-INVOKE QUOTA CHECK (prevents caching bug)
        if is_using_gemini and rate_limiter.daily_quota.is_quota_exhausted():
            logger.warning(f"⚠️ Gemini quota exhausted ({rate_limiter.daily_quota.requests_today}/{Config.RATE_LIMIT_RPD}). Switching to fallback.")
            # Force re-initialization with fallback
            self._llm = None
            self._current_model = None
            # Get fallback LLM
            fallback_llm = self._get_llm()
            return fallback_llm.invoke(*args, **kwargs)
        
        try:
            # Invoke the current LLM
            llm = self._get_llm()  # May return cached self._llm
            response = llm.invoke(*args, **kwargs)
            
            # SUCCESS: Track usage if Gemini
            if is_using_gemini:
                logger.debug(f"✅ Gemini call successful ({rate_limiter.daily_quota.requests_today}/{Config.RATE_LIMIT_RPD} RPD used)")
            
            return response
            
        except Exception as e:
            error_str = str(e).lower()
            
            # DETECT 429 QUOTA EXHAUSTION
            if is_using_gemini and ("429" in error_str or "quota" in error_str or "resourceexhausted" in error_str):
                logger.warning(f"⚠️ Gemini 429 error detected during invoke: {e}")
                
                # Mark quota as exhausted to prevent future attempts
                rate_limiter.daily_quota._count = Config.RATE_LIMIT_RPD
                logger.warning(f"📉 Marked Gemini quota as exhausted: {rate_limiter.daily_quota.requests_today}/{Config.RATE_LIMIT_RPD}")
                
                # AUTO-FALLBACK: Clear cache and retry with fallback
                if Config.LLM_PROVIDER == "hybrid":
                    logger.info("🔄 Auto-fallback to OpenAI/HuggingFace")
                    self._llm = None
                    self._current_model = None
                    fallback_llm = self._get_llm()
                    return fallback_llm.invoke(*args, **kwargs)
                else:
                    # No fallback available
                    raise Exception(f"Gemini quota exhausted (LLM_PROVIDER={Config.LLM_PROVIDER}, no fallback)") from e
            else:
                # Not a quota error, re-raise
                raise
    
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
            
            # Step 2: Consider Options (Hybrid: Hardcoded + Learned Skills)
            # Pass retrieved memories to option generation
            memories = []
            if self.reasoning_bank:
                try:
                    memories = self.reasoning_bank.retrieve(
                        context=f"{action_type} for {context.topic}",
                        topic=context.topic
                    )
                except Exception:
                    memories = []

            options = self._generate_options(context, action_type, situation_analysis, memories)
            thought_chain.thoughts.append({
                "step": "options_generation",
                "thought": f"Generated {len(options)} possible approaches (including {len(memories)} learned skills)",
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
                         situation: Dict[str, Any],
                         learned_skills: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate possible approaches based on situation + learned skills (Procedural Memory).
        """
        options = []
        
        # 1. Base Strategies (Hardcoded Best Practices)
        if action_type == "generate_question":
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
            


        # 1.5 Company-Specific Strategies
        if context.company_name:
            cn = context.company_name.lower()
            if "amazon" in cn:
                options.append({
                    "approach": "leadership_principles",
                    "description": "Probe for Amazon Leadership Principles (Customer Obsession, Ownership, Bias for Action)",
                    "suitability": 0.9
                })
            elif "google" in cn:
                options.append({
                    "approach": "gca_check",
                    "description": "Google Cognitive Ability (GCA) and 'Googliness' check",
                    "suitability": 0.9
                })
            elif "meta" in cn or "facebook" in cn:
                options.append({
                    "approach": "move_fast",
                    "description": "Focus on rapid iteration and impact",
                    "suitability": 0.9
                })
            
        # 2. Learned Skills (Procedural Memory Injection)
        if learned_skills:
            for skill in learned_skills:
                # Skill title is usually: "Progressive difficulty for Python"
                # We map it to an option
                options.append({
                    "approach": f"learned_skill:{skill.get_id()}",
                    "description": f"Skill: {skill.title} ({skill.description})",
                    "suitability": min(0.95, skill.confidence + 0.1), # Boost usage of learned skills
                    "source": "procedural_memory",
                    "content": skill.content
                })
        
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
        insights: List[str] = []
        improvements: List[str] = []
        
        try:
            # Analyze recent action quality
            action_quality = self._assess_action_quality(recent_actions)
            
            # Identify patterns
            patterns = self._identify_patterns(recent_actions)
            
            # Generate self-improvement suggestions
            suggestions = self._generate_improvement_suggestions(action_quality, patterns)
            improvements.extend(suggestions)
            
            # Calculate confidence
            confidence = self._calculate_self_confidence(action_quality, patterns)
            
            # Insights from reflection
            if action_quality["average_score"] < 0.6:
                insights.append(
                    "Performance below target - consider adjusting approach"
                )
            if patterns.get("candidate_struggling"):
                insights.append(
                    "Candidate showing signs of difficulty - increase support"
                )
            
            reflection: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "actions_reviewed": len(recent_actions),
                "insights": insights,
                "improvements": improvements,
                "confidence_in_approach": confidence,
                "action_quality": action_quality,
                "patterns": patterns
            }
            
            self.self_reflection_cache[datetime.now().isoformat()] = reflection
            
        except Exception as e:
            logger.error(f"Self-reflection error: {e}")
            reflection = {
                "timestamp": datetime.now().isoformat(),
                "actions_reviewed": len(recent_actions),
                "insights": insights,
                "improvements": improvements,
                "confidence_in_approach": 0.0,
                "error": str(e)
            }
        
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
        Uses Pydantic structured output for reliability (Architecture Audit P1).
        """
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                "skills": [],
                "experience_years": 0,
                "key_qualifications": [],
                "suggested_topics": [],
                "analysis_type": "empty"
            }
        
        # Method 1: Try Pydantic structured output (most reliable)
        if PYDANTIC_AVAILABLE and ResumeAnalysis is not None:
            try:
                llm = self._get_llm()
                if llm and hasattr(llm, 'with_structured_output'):
                    structured_llm = llm.with_structured_output(ResumeAnalysis)
                    prompt = f"""Analyze this resume and extract key information.

RESUME:
{resume_text[:3000]}

Extract: skills (technical & soft), experience_years, key_qualifications, suggested_topics, and a brief summary."""
                    
                    result = structured_llm.invoke(prompt)
                    if result:
                        return {
                            "skills": result.skills if hasattr(result, 'skills') else [],
                            "experience_years": result.experience_years if hasattr(result, 'experience_years') else 0,
                            "key_qualifications": result.key_qualifications if hasattr(result, 'key_qualifications') else [],
                            "suggested_topics": result.suggested_topics if hasattr(result, 'suggested_topics') else [],
                            "summary": result.summary if hasattr(result, 'summary') else "",
                            "analysis_type": "pydantic_structured"
                        }
            except Exception as e:
                logger.warning(f"Pydantic structured output failed: {e}, falling back to regex")
        
        # Method 2: Try LLM with manual JSON parsing (legacy fallback)
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
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                import json
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    result = json.loads(response_text[start:end])
                    result["analysis_type"] = "llm_json"
                    return cast(Dict[str, Any], result)
        except Exception as e:
            logger.warning(f"LLM JSON parsing failed: {e}, using heuristic")
        
        # Method 3: Heuristic fallback (always works)
        return self._heuristic_resume_analysis(resume_text)
    
    def _heuristic_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Keyword-based resume analysis when LLM is unavailable."""
        skills = []
        text_lower = resume_text.lower()
        
        # Comprehensive skill keywords
        skill_keywords = {
            # Programming Languages
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "java": "Java", "c++": "C++", "c#": "C#", "go": "Go", "rust": "Rust",
            "ruby": "Ruby", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
            # Frameworks & Libraries
            "react": "React", "angular": "Angular", "vue": "Vue.js", "node": "Node.js",
            "django": "Django", "flask": "Flask", "spring": "Spring", "express": "Express",
            "fastapi": "FastAPI", "next.js": "Next.js", "tensorflow": "TensorFlow",
            "pytorch": "PyTorch", "langchain": "LangChain",
            # Cloud & DevOps
            "aws": "AWS", "azure": "Azure", "gcp": "GCP", "docker": "Docker",
            "kubernetes": "Kubernetes", "terraform": "Terraform", "ci/cd": "CI/CD",
            # Databases
            "sql": "SQL", "postgresql": "PostgreSQL", "mongodb": "MongoDB",
            "redis": "Redis", "elasticsearch": "Elasticsearch",
            # AI/ML
            "machine learning": "Machine Learning", "deep learning": "Deep Learning",
            "nlp": "NLP", "computer vision": "Computer Vision", "data science": "Data Science",
            # Soft Skills & Methodologies
            "agile": "Agile", "scrum": "Scrum", "product management": "Product Management",
            "leadership": "Leadership", "communication": "Communication"
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
            approach,
            context.previous_questions # Pass history to filtering logic
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
    
    def get_progressive_question(self, topic: str, question_number: int, approach: str, previous_questions: Optional[List[str]] = None) -> str:
        """Generate progressive question using LLM with smart fallback."""
        if previous_questions is None:
            previous_questions = []
            
        # Build prompt with explicit history
        history_str = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "None"
        
        prompt = f"""[INST] You are an expert technical interviewer.
Generate a unique, challenging interview question about {topic}.

Phase: Question {question_number} of {Config.MAX_QUESTIONS}
Strategy: {approach}

PREVIOUSLY ASKED (DO NOT REPEAT):
{history_str}

CONSTRAINTS:
1. Ask something DIFFERENT from all previous questions.
2. Be specific and technical.
3. Focus on practical experience or problem-solving.

Return ONLY the question text, nothing else.
[/INST]"""
                
        try:
            llm = self._get_llm()
            if llm:
                response_obj = llm.invoke(prompt)
                response = (response_obj.content if hasattr(response_obj, 'content') else str(response_obj)).strip().replace('"', '')
                # Validate response isn't a repeat
                if response and not any(prev.lower() in response.lower() for prev in previous_questions[:3]):
                    return cast(str, response)
                logger.warning("LLM returned similar question, using fallback")
        except Exception as e:
            logger.warning(f"LLM question generation failed: {e}")
             
        # Smart fallback: Use question banks with deduplication
        fallback_questions = self._get_fallback_questions(topic)
        
        # Filter out already asked questions
        available = [q for q in fallback_questions if q not in previous_questions]
        
        if available:
            idx = (question_number - 1) % len(available)
            return available[idx]
        
        # Ultimate fallback: Generic but numbered
        return f"Question {question_number}: Describe a challenging {topic} scenario you've handled."
    
    def _get_fallback_questions(self, topic: str) -> List[str]:
        """Get fallback question bank for a topic."""
        banks = {
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
            "System Design & Architecture": [
                "Design a URL shortening service. Focus on database schema and ID generation.",
                "How does Consistent Hashing help when scaling a distributed cache?",
                "Explain the CAP theorem with a real-world example.",
                "How would you handle a distributed transaction across microservices?",
                "Design a notification system that prevents duplicate sends."
            ],
            "Cloud & DevOps (AWS/GCP/Azure)": [
                "How do you implement blue-green deployments?",
                "Explain the difference between containers and VMs.",
                "How would you design a CI/CD pipeline for a microservices app?",
                "What's your approach to infrastructure as code?",
                "How do you handle secrets management in cloud environments?"
            ],
            "Database & SQL": [
                "Explain database indexing and when to use it.",
                "What's the difference between SQL and NoSQL databases?",
                "How do you optimize a slow SQL query?",
                "Explain ACID properties with examples.",
                "How do you handle database migrations in production?"
            ]
        }
        
        # Try exact match first
        if topic in banks:
            return banks[topic]
        
        # Try partial match
        topic_lower = topic.lower()
        for key, questions in banks.items():
            if any(word in topic_lower for word in key.lower().split()):
                return questions
        
        # Generic fallback
        return [
            f"What's the most challenging {topic} problem you've solved?",
            f"How do you stay updated with developments in {topic}?",
            f"Describe a recent project involving {topic}.",
            f"What best practices do you follow when working with {topic}?",
            f"How would you explain {topic} to a junior developer?"
        ]
    
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
        
        return cast(float, max(0.0, min(1.0, base_confidence)))
    
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
            return cast(str, max(other_options, key=lambda x: x.get("suitability", 0))["approach"])
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
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Validate response isn't empty
            if not response_text or len(response_text) < 10:
                return {"score": 7, "feedback": "LLM returned empty critique."}

            import json
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                return cast(Dict[str, Any], json.loads(response_text[start:end]))
            
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
            
            response_obj = llm.invoke(prompt)
            revised = (response_obj.content if hasattr(response_obj, 'content') else str(response_obj)).strip()
            # Remove quotes if present
            if revised.startswith('"') and revised.endswith('"'):
                revised = revised[1:-1]
            return cast(str, revised)

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
                response_text = response.content if hasattr(response, 'content') else str(response)
            
                # 3. Parse JSON or use heuristic
                import json
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    try:
                        result = json.loads(response_text[start:end])
                    except json.JSONDecodeError:
                        result = {"decision": heuristic_decision, "ui_label": "Standard Mode"}
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
    

    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for self-monitoring"""
        return {
            "metrics": self.performance_metrics,
            "thought_history_size": len(self.thought_history),
            "reflection_cache_size": len(self.self_reflection_cache),
            "decision_log_size": len(self.decision_log),
            "llm_status": "connected" if self._llm else "disconnected"
        }
