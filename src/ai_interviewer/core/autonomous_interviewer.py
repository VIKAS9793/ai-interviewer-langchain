"""
Autonomous AI Interviewer Agent
Human-like, self-thinking, resilient interview conductor

This is the main agent that orchestrates:
- Autonomous reasoning for decision-making
- Human-like conversation flow
- Adaptive interview progression
- Self-monitoring and improvement
"""

import logging
import time
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

from .autonomous_reasoning_engine import (
    AutonomousReasoningEngine,
    InterviewContext,
    CandidateState,
    ThoughtChain,
    ReasoningMode
)


from .reflect_agent import ReflectAgent
from .context_engineer import KnowledgeGrounding
from .static_analyzer import StaticCodeAnalyzer
from src.ai_interviewer.utils.prompts import CODE_EVALUATION_PROMPT, DEFAULT_EVALUATION_PROMPT

logger = logging.getLogger(__name__)


class SemanticRelevanceChecker:
    """
    Semantic relevance checker using Sentence Transformers.
    Uses embedding similarity to verify answer addresses the question.
    
    Features:
    - Lazy model loading
    - Embedding cache (avoid recomputing for same text)
    - Similarity cache (avoid recomputing for same Q&A pairs)
    """
    
    MAX_EMBEDDING_CACHE_SIZE = 100
    MAX_SIMILARITY_CACHE_SIZE = 50
    
    def __init__(self):
        self._model = None
        self._available = True
        self._embedding_cache: Dict[str, Any] = {}  # text -> embedding
        self._similarity_cache: Dict[str, float] = {}  # "q|||a" -> similarity
        self._cache_stats = {"hits": 0, "misses": 0}
        
    def _get_model(self):
        """Lazy load the sentence transformer model"""
        if self._model is None and self._available:
            try:
                from sentence_transformers import SentenceTransformer
                # Use a small, fast model suitable for HF Spaces
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ SemanticRelevanceChecker: Model loaded (all-MiniLM-L6-v2)")
            except ImportError:
                logger.warning("sentence-transformers not installed, falling back to keyword matching")
                self._available = False
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
                self._available = False
        return self._model
    
    def _get_embedding(self, text: str):
        """Get embedding for text, using cache if available"""
        if text in self._embedding_cache:
            self._cache_stats["hits"] += 1
            return self._embedding_cache[text]
        
        self._cache_stats["misses"] += 1
        model = self._get_model()
        if model is None:
            return None
        
        embedding = model.encode(text, convert_to_tensor=True)
        
        # Cache with LRU-style eviction (remove oldest if full)
        if len(self._embedding_cache) >= self.MAX_EMBEDDING_CACHE_SIZE:
            # Remove first (oldest) item
            oldest_key = next(iter(self._embedding_cache))
            del self._embedding_cache[oldest_key]
        
        self._embedding_cache[text] = embedding
        return embedding
    
    def compute_similarity(self, question: str, answer: str) -> float:
        """
        Compute semantic similarity between question and answer.
        Returns 0.0-1.0 where higher means more relevant.
        Uses caching to avoid recomputation.
        """
        # Check similarity cache first
        cache_key = f"{question}|||{answer}"
        if cache_key in self._similarity_cache:
            logger.debug(f"📦 Similarity cache HIT")
            return self._similarity_cache[cache_key]
        
        model = self._get_model()
        if model is None:
            return -1.0  # Signal that semantic check is unavailable
        
        try:
            # Get cached embeddings
            q_embedding = self._get_embedding(question)
            a_embedding = self._get_embedding(answer)
            
            if q_embedding is None or a_embedding is None:
                return -1.0
            
            # Compute cosine similarity
            from sentence_transformers.util import cos_sim
            similarity = cos_sim(q_embedding, a_embedding).item()
            similarity = max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
            # Cache the similarity result
            if len(self._similarity_cache) >= self.MAX_SIMILARITY_CACHE_SIZE:
                oldest_key = next(iter(self._similarity_cache))
                del self._similarity_cache[oldest_key]
            self._similarity_cache[cache_key] = similarity
            
            return similarity
        except Exception as e:
            logger.warning(f"Semantic similarity computation failed: {e}")
            return -1.0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "embedding_cache_size": len(self._embedding_cache),
            "similarity_cache_size": len(self._similarity_cache),
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "hit_rate": self._cache_stats["hits"] / max(1, self._cache_stats["hits"] + self._cache_stats["misses"])
        }

# Global instance for reuse
_semantic_checker = None

def get_semantic_checker() -> SemanticRelevanceChecker:
    """Get or create the global semantic checker instance"""
    global _semantic_checker
    if _semantic_checker is None:
        _semantic_checker = SemanticRelevanceChecker()
    return _semantic_checker


class InterviewPhase(Enum):
    """Interview phases"""
    INTRODUCTION = "introduction"
    WARM_UP = "warm_up"
    CORE_ASSESSMENT = "core_assessment"
    DEEP_DIVE = "deep_dive"
    CONCLUSION = "conclusion"


@dataclass
class InterviewSession:
    """Complete interview session state"""
    session_id: str
    candidate_name: str
    topic: str
    phase: InterviewPhase = InterviewPhase.INTRODUCTION
    question_number: int = 0
    max_questions: int = 5
    qa_pairs: List[Dict[str, Any]] = field(default_factory=list)
    current_question: str = ""
    current_answer: str = ""
    performance_history: List[float] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    candidate_state: CandidateState = CandidateState.NEUTRAL
    thought_chains: List[ThoughtChain] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    interview_complete: bool = False
    final_report: Optional[str] = None


class AutonomousInterviewer:
    """
    Autonomous AI Interviewer with Human-Like Capabilities
    
    Key Features:
    1. SELF-THINKING: Uses Chain-of-Thought before every action
    2. LOGICAL REASONING: Analyzes situations and makes reasoned decisions
    3. SELF-RESILIENT: Recovers gracefully from errors
    4. HUMAN-LIKE: Natural conversation, empathy, adaptability
    """
    
    def __init__(self, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
        self.model_name = model_name
        self.reasoning_engine = AutonomousReasoningEngine(model_name)
        self.active_sessions: Dict[str, InterviewSession] = {}
        self._llm = None
        
        # Interview personality traits
        self.personality = {
            "warmth": 0.7,
            "professionalism": 0.9,
            "adaptability": 0.8,
            "patience": 0.8,
            "encouragement_level": 0.6
        }
        
        # Self-monitoring
        self.interview_metrics = {
            "sessions_conducted": 0,
            "avg_session_duration": 0.0,
            "avg_candidate_satisfaction": 0.0,
            "successful_adaptations": 0
        }
        
        
        # Hybrid Research - Reflect Agent (Shadow Mode)
        self.reflect_agent = None
        try:
            self.reflect_agent = ReflectAgent()
        except Exception as e:
            logger.warning(f"ReflectAgent failed to init: {e}")
        
        # Knowledge Grounding for answer verification
        self.knowledge_grounding = None
        try:
            self.knowledge_grounding = KnowledgeGrounding()
        except Exception as e:
            logger.warning(f"KnowledgeGrounding failed to init: {e}")

        logger.info("🤖 Autonomous Interviewer initialized")
    
    def set_model(self, model_id: str) -> None:
        """Set the model to use for LLM inference"""
        if model_id != self.model_name:
            self.model_name = model_id
            self._llm = None  # Reset LLM to force re-initialization
            logger.info(f"🔄 Model changed to: {model_id}")
    
    def _get_llm(self) -> HuggingFaceEndpoint:
        """Get Cloud LLM with lazy loading"""
        if self._llm is None:
            try:
                # CLOUD ADAPTATION: Use Hugging Face Serverless Inference
                # Requires HF_TOKEN in environment variables
                token = os.environ.get("HF_TOKEN")
                if not token:
                    logger.warning("⚠️ HF_TOKEN not found! Falling back to public endpoints (may be rate limited).")
                
                self._llm = HuggingFaceEndpoint(
                    repo_id=self.model_name,
                    task="text-generation",
                    max_new_tokens=512,
                    top_k=50,
                    temperature=0.4,
                    huggingfacehub_api_token=token
                )
                logger.info(f"☁️ Connected to Hugging Face Cloud Inference ({self.model_name})")
            except Exception as e:
                logger.error(f"Failed to initialize Cloud LLM: {e}")
        return self._llm
    
    def _get_evaluation_llm(self) -> HuggingFaceEndpoint:
        """
        Get dedicated LLM for evaluation.
        STABILITY FIX: Reusing primary LLM connection.
        Dedicated models (Qwen/Mistral) were failing API checks on Cloud Free Tier.
        """
        logger.info(f"📊 Using Primary LLM for Evaluation (Stability Mode)")
        return self._get_llm()
    
    # ==================== INTERVIEW LIFECYCLE ====================
    
    def start_interview(self, topic: str, candidate_name: str) -> Dict[str, Any]:
        """
        Start a new interview session with autonomous reasoning
        """
        session_id = str(uuid.uuid4())[:8]
        
        # Create session
        session = InterviewSession(
            session_id=session_id,
            candidate_name=candidate_name,
            topic=topic
        )
        
        self.active_sessions[session_id] = session
        
        # AUTONOMOUS: Think before greeting
        context = self._build_context(session)
        greeting_thought = self.reasoning_engine.think_before_acting(
            context, "generate_greeting"
        )
        session.thought_chains.append(greeting_thought)
        
        # Generate personalized greeting
        greeting = self._generate_human_greeting(session, greeting_thought)
        
        # Generate first question with reasoning
        first_question_result = self._generate_next_question_autonomous(session)
        
        session.phase = InterviewPhase.WARM_UP
        session.question_number = 1
        session.current_question = first_question_result["question"]
        
        logger.info(f"🎤 Started interview: {session_id} for {candidate_name} on {topic}")
        
        return {
            "status": "started",
            "session_id": session_id,
            "greeting": greeting,
            "first_question": first_question_result["question"],
            "phase": session.phase.value,
            "reasoning": {
                "thought_chain_id": greeting_thought.reasoning_id,
                "approach": first_question_result.get("approach"),
                "confidence": first_question_result.get("confidence", 0.7)
            },
            "autonomous_features": {
                "self_thinking": True,
                "logical_reasoning": True,
                "adaptive_behavior": True,
                "human_like_conduct": True,
                "self_resilient": True
            }
        }
    
    def process_answer(self, session_id: str, answer: str) -> Dict[str, Any]:
        """
        Process candidate's answer with autonomous reasoning
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.current_answer = answer
        
        # AUTONOMOUS: Analyze and evaluate with reasoning
        context = self._build_context(session)
        
        # Step 1: Think about how to evaluate
        eval_thought = self.reasoning_engine.think_before_acting(
            context, "evaluate"
        )
        session.thought_chains.append(eval_thought)
        
        # Step 2: Perform evaluation with reasoning
        evaluation = self._evaluate_answer_autonomous(session, eval_thought)
        
        # Step 3: Update candidate state based on evaluation
        self._update_candidate_state(session, evaluation)
        
        # Step 4: Store Q&A pair
        qa_pair = {
            "question_number": session.question_number,
            "question": session.current_question,
            "answer": answer,
            "evaluation": evaluation,
            "candidate_state": session.candidate_state.value,
            "thought_chain_id": eval_thought.reasoning_id
        }
        session.qa_pairs.append(qa_pair)
        session.performance_history.append(evaluation.get("score", 5))
        
        # Step 5: Self-reflect on interview progress
        if len(session.qa_pairs) >= 2:
            reflection = self.reasoning_engine.self_reflect(session.qa_pairs)
            self._apply_reflection_insights(session, reflection)
        
        # Step 6: Decide next action
        if session.question_number >= session.max_questions:
            return self._complete_interview(session)
        
        # Step 7: Generate next question with full autonomous reasoning
        next_question_result = self._generate_next_question_autonomous(session)
        session.question_number += 1
        session.current_question = next_question_result["question"]
        
        # Update phase
        session.phase = self._determine_phase(session)
        
        return {
            "status": "continue",
            "evaluation": evaluation,
            "feedback": self._generate_human_feedback(session, evaluation),
            "next_question": next_question_result["question"],
            "question_number": session.question_number,
            "phase": session.phase.value,
            "candidate_state": session.candidate_state.value,
            "reasoning": {
                "evaluation_approach": eval_thought.conclusion,
                "question_approach": next_question_result.get("approach"),
                "adaptations_made": next_question_result.get("adaptations", []),
                "confidence": next_question_result.get("confidence", 0.7),
                "thought_chain_id": next_question_result.get("thought_chain_id", "N/A")
            },
            "progress": {
                "completed": session.question_number - 1,
                "total": session.max_questions,
                "avg_score": sum(session.performance_history) / len(session.performance_history) if session.performance_history else 0
            }
        }
    
    def _complete_interview(self, session: InterviewSession) -> Dict[str, Any]:
        """Complete interview with comprehensive report"""
        session.interview_complete = True
        session.phase = InterviewPhase.CONCLUSION
        
        # AUTONOMOUS: Think about final report
        context = self._build_context(session)
        report_thought = self.reasoning_engine.think_before_acting(
            context, "generate_report"
        )
        session.thought_chains.append(report_thought)
        
        # Generate comprehensive report
        final_report = self._generate_final_report_autonomous(session, report_thought)
        session.final_report = final_report
        
        # Update metrics
        self.interview_metrics["sessions_conducted"] += 1
        session_duration = time.time() - session.start_time
        self._update_session_metrics(session, session_duration)
        
        return {
            "status": "completed",
            "session_id": session.session_id,
            "final_report": final_report,
            "summary": {
                "questions_asked": len(session.qa_pairs),
                "avg_score": sum(session.performance_history) / len(session.performance_history) if session.performance_history else 0,
                "strengths": session.strengths[:3],
                "areas_for_improvement": session.knowledge_gaps[:3],
                "candidate_progression": self._analyze_progression(session)
            },
            "autonomous_insights": {
                "thought_chains_used": len(session.thought_chains),
                "adaptations_made": self.reasoning_engine.performance_metrics["adaptation_count"],
                "self_reflections": len(self.reasoning_engine.self_reflection_cache)
            }
        }
    
    # ==================== AUTONOMOUS QUESTION GENERATION ====================
    
    def _generate_next_question_autonomous(self, session: InterviewSession) -> Dict[str, Any]:
        """
        Generate next question with full autonomous reasoning
        
        This is where the AI truly "thinks" like a human interviewer
        """
        context = self._build_context(session)
        
        # Step 1: Think about what question to ask
        thought_chain = self.reasoning_engine.think_before_acting(
            context, "generate_question"
        )
        session.thought_chains.append(thought_chain)
        
        # Step 2: Apply adaptations based on candidate state
        adaptations = self.reasoning_engine.adapt_to_situation(context)
        
        # Step 2b: Fairness Reflection (Safe Shadow Mode)
        if self.reflect_agent and thought_chain.conclusion:
            try:
                # Just self-reflect on the proposed approach for now
                pass 
            except Exception:
                pass
        
        # Step 3: Generate human-like question
        question_result = self.reasoning_engine.generate_human_like_question(
            context, thought_chain
        )
        
        # Step 4: If LLM available, enhance with dynamic generation
        enhanced_question = self._enhance_question_with_llm(
            session, question_result, adaptations
        )
        
        return {
            "question": enhanced_question,
            "approach": thought_chain.conclusion,
            "confidence": thought_chain.confidence,
            "adaptations": adaptations,
            "thought_chain_id": thought_chain.reasoning_id
        }
    
    def _enhance_question_with_llm(self, session: InterviewSession,
                                   question_result: Dict[str, Any],
                                   adaptations: Dict[str, Any]) -> str:
        """
        Return clean question from reasoning engine.
        
        Note: LLM enhancement disabled to ensure clean output.
        The reasoning engine already produces quality questions.
        """
        return question_result["question"]
    
    # ==================== AUTONOMOUS EVALUATION ====================
    
    def _evaluate_answer_autonomous(self, session: InterviewSession,
                                   thought_chain: ThoughtChain) -> Dict[str, Any]:
        """
        Evaluate answer with autonomous reasoning
        
        Combines:
        - Heuristic evaluation (fast, reliable)
        - LLM evaluation (nuanced, detailed)
        - Reasoning engine insights
        """
        answer = session.current_answer
        question = session.current_question
        topic = session.topic
        
        # MERGED EVALUATION LOGIC
        # ---------------------------------------------------------
        # 1. Detect if this is a code submission
        # ROLLBACK v2.3: Disabled Code Evaluation due to API limits. Always False.
        is_code = False
        
        # Infer language from topic
        language = "python"
        
        static_analysis = {"valid": False, "metrics": {}} # Mock empty analysis for rollback
        if "javascript" in topic.lower() or "frontend" in topic.lower():
            language = "javascript"
        elif "sql" in topic.lower():
            language = "sql"
        elif "java" in topic.lower() and "javascript" not in topic.lower():
            language = "java"
            
        static_analysis = StaticCodeAnalyzer.analyze(answer, language=language)
        if static_analysis.get("valid") and static_analysis.get("metrics"):
             # Heuristic: If it has valid metrics (complexity etc), treat as code
             # We can refine this by checking if metrics['loc'] > 1 or similar
             is_code = True
             logger.info(f"💻 Code submission detected: {static_analysis['metrics']}")
        
        # 2. Heuristic Evaluation
        heuristic_eval = self._heuristic_evaluation(answer, topic, question)
        
        # 3. LLM Evaluation (Code vs Text)
        llm_eval = self._llm_evaluation(question, answer, topic, session, 
                                      is_code=is_code, 
                                      analysis=static_analysis)
        
        # 4. Knowledge Grounding (Skip for code usually, or apply mainly to comments?)
        # For now, we apply it if it's text, or if we want to check code comments against docs.
        # Let's keep it optional but log warnings.
        grounding_result = None
        if self.knowledge_grounding and not is_code: # Skip grounding for code for MVP
            try:
                grounding_result = self.knowledge_grounding.verify_answer(topic, question, answer)
            except Exception as e:
                logger.warning(f"Knowledge grounding failed: {e}")

        # 5. Merge evaluations
        merged_eval = self._merge_evaluations(heuristic_eval, llm_eval, thought_chain)
        
        if grounding_result:
            merged_eval["grounding"] = grounding_result
            
        if is_code:
            merged_eval["is_code"] = True
            merged_eval["static_analysis"] = static_analysis.get("metrics")
            # If static analysis failed (syntax error), override score
            if not static_analysis.get("valid"):
                 merged_eval["score"] = 1.0
                 merged_eval["brief_feedback"] = f"Syntax Error: {static_analysis.get('error')}"

        return merged_eval
    
    def _heuristic_evaluation(self, answer: str, topic: str, question: str = "") -> Dict[str, Any]:
        """Fast heuristic evaluation (always works)"""
        if not answer or len(answer.strip()) < 10:
            return {
                "score": 2.0,
                "technical_accuracy": 0.2,
                "completeness": 0.1,
                "clarity": 0.3,
                "relevance": 0.0,
                "source": "heuristic"
            }
        
        # CRITICAL: Question-Answer Relevance Check
        relevance_score = self._check_answer_relevance(question, answer)
        if relevance_score < 0.3:  # Answer is off-topic
            return {
                "score": 2.0,
                "technical_accuracy": 0.1,
                "completeness": 0.1,
                "clarity": 0.3,
                "relevance": relevance_score,
                "source": "heuristic",
                "warning": "Answer does not appear to address the question asked"
            }
        
        # Length-based scoring (BOOSTED for comprehensive answers)
        word_count = len(answer.split())
        # More generous: 100+ words gets full points, scaled linearly
        length_score = min(word_count / 50, 1.0) * 5  # Max 5 points (was 4)
        
        # Keyword matching (topic relevance)
        keywords = self._get_topic_keywords(topic)
        keyword_count = sum(1 for kw in keywords if kw.lower() in answer.lower())
        keyword_score = min(keyword_count * 0.8, 3.0)  # Max 3 points
        
        # Structure indicators (BOOSTED)
        structure_score = 0
        if any(word in answer.lower() for word in ["first", "second", "because", "therefore", "however"]):
            structure_score += 1.5
        if any(char in answer for char in ["1.", "2.", "3.", "-", "•", ":"]):
            structure_score += 1.5
        structure_score = min(structure_score, 3.0)  # Max 3 points (was 2)
        
        # Example usage and practical application
        example_score = 0
        if any(word in answer.lower() for word in ["example", "for instance", "such as", "like", "consider"]):
            example_score = 2.0  # Was 1.5
        
        # DEPTH BONUS: Comprehensive answers deserve extra credit
        depth_bonus = 0
        if word_count > 150 and structure_score > 1:
            depth_bonus = 1.5  # Bonus for truly comprehensive answers
        
        # Apply relevance penalty
        relevance_multiplier = max(relevance_score, 0.3)
        base_score = length_score + keyword_score + structure_score + example_score + depth_bonus
        total_score = min(base_score * relevance_multiplier, 10)
        
        return {
            "score": round(total_score, 1),
            "technical_accuracy": min(keyword_score / 3, 1.0) * relevance_multiplier,
            "completeness": min(length_score / 5, 1.0),
            "clarity": min((structure_score + 0.5) / 3.5, 1.0),
            "relevance": relevance_score,
            "source": "heuristic",
            "details": {
                "word_count": word_count,
                "keywords_found": keyword_count,
                "has_structure": structure_score > 0,
                "has_examples": example_score > 0,
                "depth_bonus": depth_bonus > 0,
                "relevance_check": relevance_score
            }
        }
    
    def _check_answer_relevance(self, question: str, answer: str) -> float:
        """
        Check if answer is relevant to the question asked.
        Uses semantic similarity (embedding-based) with fallback to keyword matching.
        """
        if not question:
            return 1.0  # No question to check against
        
        # Try semantic similarity first (embedding-based)
        semantic_checker = get_semantic_checker()
        semantic_score = semantic_checker.compute_similarity(question, answer)
        
        if semantic_score >= 0:  # Semantic check succeeded
            logger.info(f"📊 Semantic similarity: {semantic_score:.2f}")
            # Semantic similarity threshold: below 0.3 is definitely off-topic
            if semantic_score < 0.25:
                logger.warning(f"⚠️ Answer appears OFF-TOPIC (semantic: {semantic_score:.2f})")
            return semantic_score
        
        # Fallback to keyword matching if semantic check unavailable
        logger.info("📊 Using keyword-based relevance (semantic unavailable)")
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Extract question keywords (skip common words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 
                      'can', 'you', 'explain', 'describe', 'tell', 'me', 'about', 'between',
                      'and', 'or', 'in', 'of', 'to', 'for', 'with', 'do', 'does', 'your'}
        
        question_words = set(question_lower.split()) - stop_words
        answer_words = set(answer_lower.split())
        
        # Check keyword overlap
        if not question_words:
            return 1.0
        
        overlap = question_words & answer_words
        relevance_ratio = len(overlap) / len(question_words)
        
        # Boost for key technical terms from question appearing in answer
        technical_terms = [w for w in question_words if len(w) > 5]
        technical_overlap = sum(1 for term in technical_terms if term in answer_lower)
        technical_boost = min(technical_overlap * 0.2, 0.4) if technical_terms else 0
        
        return min(relevance_ratio + technical_boost, 1.0)
    
    def _llm_evaluation(self, question: str, answer: str, 
                       topic: str, session: InterviewSession,
                       is_code: bool = False,
                       analysis: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        LLM-based evaluation using Prometheus-style rubric scoring.
        Uses dedicated evaluation LLM (Qwen2.5) with 1-5 scale for reliability.
        """
        try:
            # Use dedicated evaluation LLM for better calibration
            llm = self._get_evaluation_llm()
            if not llm:
                return None
            
            # Select prompt based on content type
            if is_code and analysis and analysis.get("valid"):
                # Use Code Evaluation Prompt
                metrics = analysis.get("metrics", {})
                prompt_text = CODE_EVALUATION_PROMPT.format(
                    topic=topic,
                    question=question,
                    language=metrics.get("language", "python"),
                    code=answer,
                    complexity=metrics.get("cyclomatic_complexity", "N/A"),
                    nesting=metrics.get("max_nesting_depth", "N/A")
                )
                logger.info("🧪 Using CODE evaluation prompt")
            else:
                # Use Default Text Prompt
                prompt_text = DEFAULT_EVALUATION_PROMPT.format(
                    topic=topic,
                    question=question,
                    answer=answer
                )
                logger.info("📝 Using DEFAULT text evaluation prompt")
            
            # Call LLM
            response = llm.invoke(prompt_text)
            # Legacy prompt construction removed. 
            # Response is already obtained from llm.invoke(prompt_text) above.

            
            # Parse JSON response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                evaluation = json.loads(response[json_start:json_end])
                evaluation["source"] = "llm_qwen"
                evaluation["scale"] = 5  # Mark as 1-5 scale
                return evaluation
            
            return None
            
        except Exception as e:
            logger.warning(f"LLM evaluation failed: {e}")
            return None
    
    def _merge_evaluations(self, heuristic: Dict[str, Any],
                          llm_eval: Optional[Dict[str, Any]],
                          thought_chain: ThoughtChain) -> Dict[str, Any]:
        """
        Merge heuristic and LLM evaluations intelligently.
        
        Uses 60/40 weighting (LLM/Heuristic) with scale normalization.
        LLM uses 1-5 scale, heuristic uses 1-10 scale.
        Final output is 1-10 scale for UI consistency.
        """
        if llm_eval is None:
            # Only heuristic available - use as-is (already 1-10 scale)
            return {
                **heuristic,
                "confidence": 0.5,  # Lower confidence without LLM
                "evaluation_method": "heuristic_only",
                "scale": 10
            }
        
        # Rebalanced weights (60/40 - more trust in improved heuristics)
        llm_weight = 0.6
        heuristic_weight = 0.4
        
        # Get scores with scale normalization
        # LLM returns 1-5 scale, convert to 1-10
        llm_score = llm_eval.get("score", 3) * 2  # 1-5 -> 2-10
        heuristic_score = heuristic.get("score", 5)  # Already 1-10
        
        # Weighted merge
        merged_score = (
            llm_score * llm_weight +
            heuristic_score * heuristic_weight
        )
        
        # Confidence based on evaluation method
        confidence = 0.85 if llm_eval.get("source") == "llm_qwen" else 0.75
        
        return {
            "score": round(merged_score, 1),
            "technical_accuracy": llm_eval.get("technical_accuracy", heuristic.get("technical_accuracy", 0.5)),
            "understanding_depth": llm_eval.get("understanding_depth", 0.5),
            "communication": llm_eval.get("communication", heuristic.get("clarity", 0.5)),
            "practical_application": llm_eval.get("practical_application", 0.5),
            "completeness": heuristic.get("completeness", 0.5),
            "relevance": heuristic.get("relevance", 1.0),
            "strengths": llm_eval.get("strengths", ["Good attempt"]),
            "improvements": llm_eval.get("improvements", ["More detail needed"]),
            "knowledge_gaps": llm_eval.get("knowledge_gaps", []),
            "brief_feedback": llm_eval.get("brief_feedback", ""),
            "confidence": confidence,
            "evaluation_method": "merged_hybrid",
            "reasoning_approach": thought_chain.conclusion,
            "scale": 10,
            "llm_raw_score": llm_eval.get("score", 3),
            "heuristic_raw_score": heuristic.get("score", 5)
        }
    
    # ==================== HUMAN-LIKE INTERACTIONS ====================
    
    def _generate_human_greeting(self, session: InterviewSession,
                                thought_chain: ThoughtChain) -> str:
        """Generate warm, professional greeting"""
        greetings = [
            f"Hi {session.candidate_name}! I'm excited to learn about your experience with {session.topic}.",
            f"Welcome, {session.candidate_name}. Thank you for joining today. Let's explore your knowledge of {session.topic} together.",
            f"Hello {session.candidate_name}! I'm looking forward to our conversation about {session.topic}. Let's have a great discussion.",
        ]
        
        # Select based on personality warmth
        import random
        greeting = random.choice(greetings)
        
        # Add encouragement based on reasoning
        if thought_chain.mode == ReasoningMode.EMPATHETIC:
            greeting += " There are no wrong answers - I'm most interested in how you think."
        
        return greeting
    
    def _generate_human_feedback(self, session: InterviewSession,
                                evaluation: Dict[str, Any]) -> str:
        """Generate human-like feedback based on evaluation"""
        score = evaluation.get("score", 5)
        
        # Acknowledgment based on score
        if score >= 8:
            acknowledgments = [
                "That's an excellent answer!",
                "Great explanation!",
                "You've clearly mastered this concept."
            ]
        elif score >= 6:
            acknowledgments = [
                "Good thinking.",
                "That covers the main points well.",
                "I can see your understanding here."
            ]
        elif score >= 4:
            acknowledgments = [
                "Thanks for that perspective.",
                "I see your approach.",
                "Let me build on that."
            ]
        else:
            acknowledgments = [
                "Thank you for sharing your thoughts.",
                "I appreciate the effort.",
                "Let's explore this a bit more."
            ]
        
        import random
        feedback = random.choice(acknowledgments)
        
        # Add specific feedback if available
        if evaluation.get("brief_feedback"):
            feedback += f" {evaluation['brief_feedback']}"
        
        # Add encouragement if struggling
        if session.candidate_state == CandidateState.STRUGGLING:
            feedback += " Don't worry - we all have areas to grow in."
        
        return feedback
    
    # ==================== STATE MANAGEMENT ====================
    
    def _update_candidate_state(self, session: InterviewSession,
                               evaluation: Dict[str, Any]):
        """Update candidate state based on recent performance"""
        score = evaluation.get("score", 5)
        history = session.performance_history
        
        # Determine state based on recent trend
        if len(history) >= 2:
            recent_avg = sum(history[-2:]) / 2
            trend = score - recent_avg
            
            if trend > 1.5:
                session.candidate_state = CandidateState.IMPROVING
            elif trend < -1.5:
                session.candidate_state = CandidateState.DECLINING
            elif score >= 8:
                session.candidate_state = CandidateState.EXCELLING
            elif score <= 4:
                session.candidate_state = CandidateState.STRUGGLING
            else:
                session.candidate_state = CandidateState.NEUTRAL
        elif score >= 7:
            session.candidate_state = CandidateState.CONFIDENT
        elif score <= 4:
            session.candidate_state = CandidateState.NERVOUS
        
        # Update knowledge gaps and strengths
        gaps = evaluation.get("knowledge_gaps", [])
        strengths = evaluation.get("strengths", [])
        
        session.knowledge_gaps.extend(gaps)
        session.strengths.extend(strengths)
        
        # Deduplicate
        session.knowledge_gaps = list(set(session.knowledge_gaps))
        session.strengths = list(set(session.strengths))
    
    def _apply_reflection_insights(self, session: InterviewSession,
                                  reflection: Dict[str, Any]):
        """Apply insights from self-reflection to improve interview"""
        improvements = reflection.get("improvements", [])
        
        for improvement in improvements:
            if "simplifying" in improvement.lower():
                # Adjust for next question
                self.personality["patience"] = min(1.0, self.personality["patience"] + 0.1)
            if "encouraging" in improvement.lower():
                self.personality["encouragement_level"] = min(1.0, self.personality["encouragement_level"] + 0.1)
    
    def _determine_phase(self, session: InterviewSession) -> InterviewPhase:
        """Determine current interview phase"""
        progress = session.question_number / session.max_questions
        
        if progress <= 0.2:
            return InterviewPhase.WARM_UP
        elif progress <= 0.6:
            return InterviewPhase.CORE_ASSESSMENT
        elif progress <= 0.9:
            return InterviewPhase.DEEP_DIVE
        else:
            return InterviewPhase.CONCLUSION
    
    def _build_context(self, session: InterviewSession) -> InterviewContext:
        """Build context for reasoning engine"""
        return InterviewContext(
            session_id=session.session_id,
            candidate_name=session.candidate_name,
            topic=session.topic,
            question_number=session.question_number,
            max_questions=session.max_questions,
            performance_history=session.performance_history,
            knowledge_gaps=session.knowledge_gaps,
            strengths=session.strengths,
            candidate_state=session.candidate_state,
            conversation_flow=[
                {"q": qa["question"][:50], "score": qa["evaluation"].get("score", 5)}
                for qa in session.qa_pairs[-3:]
            ]
        )
    
    # ==================== REPORT GENERATION ====================
    
    def _generate_final_report_autonomous(self, session: InterviewSession,
                                         thought_chain: ThoughtChain) -> str:
        """Generate comprehensive final report with reasoning"""
        avg_score = sum(session.performance_history) / len(session.performance_history) if session.performance_history else 0
        
        # Determine overall assessment
        if avg_score >= 8:
            assessment = "Strong Hire"
            summary = "Exceptional performance demonstrating deep technical knowledge and excellent communication."
        elif avg_score >= 6:
            assessment = "Hire"
            summary = "Good performance with solid technical foundation and room for growth."
        elif avg_score >= 4:
            assessment = "Maybe"
            summary = "Average performance with potential but significant gaps to address."
        else:
            assessment = "No Hire"
            summary = "Below expectations. Needs significant improvement in core areas."
        
        report = f"""
# Interview Report

## Candidate: {session.candidate_name}
## Topic: {session.topic}
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Overview
- **Questions Asked:** {len(session.qa_pairs)}
- **Average Score:** {avg_score:.1f}/10
- **Assessment:** {assessment}
- **Summary:** {summary}

---

## Performance Summary

| Metric | Score |
|--------|-------|
| Average Score | {avg_score:.1f}/10 |
| Questions Completed | {len(session.qa_pairs)}/{session.max_questions} |
| Final State | {session.candidate_state.value} |

---

## Strengths Identified
{chr(10).join(f'- {s}' for s in session.strengths[:5]) if session.strengths else '- No specific strengths identified'}

## Areas for Improvement
{chr(10).join(f'- {g}' for g in session.knowledge_gaps[:5]) if session.knowledge_gaps else '- No specific gaps identified'}

---

## Question-by-Question Analysis

"""
        for i, qa in enumerate(session.qa_pairs, 1):
            score = qa["evaluation"].get("score", 0)
            report += f"""### Question {i}
**Q:** {qa['question'][:100]}...
**Score:** {score}/10
**State:** {qa.get('candidate_state', 'neutral')}

"""
        
        report += f"""
---

## Recommendations
{self._generate_dynamic_recommendations(session, avg_score)}

---

## Interview Quality Metrics
- Thought chains used: {len(session.thought_chains)}
- Adaptations made: {self.reasoning_engine.performance_metrics['adaptation_count']}
- Self-reflections: {len(self.reasoning_engine.self_reflection_cache)}

*This report was generated by an autonomous AI interviewer with self-thinking capabilities.*
"""
        return report
    
    def _generate_dynamic_recommendations(self, session: InterviewSession, avg_score: float) -> str:
        """Generate recommendations based on actual performance"""
        recommendations = []
        
        if avg_score >= 8:
            # High performer - positive recommendations
            recommendations.append("🎉 **Excellent performance!** Consider mentoring others in your strong areas.")
            if session.strengths:
                recommendations.append(f"💪 Continue building on your strengths: {', '.join(session.strengths[:2])}")
            recommendations.append("📚 Explore advanced topics to further deepen expertise")
        elif avg_score >= 6:
            # Good performer
            recommendations.append("👍 Good foundation - keep practicing to reach excellence")
            if session.knowledge_gaps:
                recommendations.append(f"📖 Focus on improving: {', '.join(session.knowledge_gaps[:2])}")
            else:
                recommendations.append("📖 Continue practicing with more complex scenarios")
        else:
            # Needs improvement
            if session.knowledge_gaps:
                recommendations.append(f"⚠️ Priority areas to study: {', '.join(session.knowledge_gaps[:3])}")
            recommendations.append(f"📚 Review {session.topic} fundamentals")
            recommendations.append("💡 Practice explaining technical concepts out loud")
        
        return "\n".join(f"{i+1}. {r}" for i, r in enumerate(recommendations))
    
    # ==================== HELPER METHODS ====================
    
    def _get_topic_keywords(self, topic: str) -> List[str]:
        """Get relevant keywords for topic"""
        keywords = {
            "JavaScript/Frontend Development": [
                "function", "variable", "object", "array", "DOM", "event",
                "async", "await", "promise", "callback", "closure", "scope",
                "prototype", "class", "component", "state", "props", "hooks"
            ],
            "Python/Backend Development": [
                "function", "class", "method", "import", "module", "def",
                "return", "exception", "decorator", "generator", "list",
                "dictionary", "tuple", "async", "await", "api", "database"
            ],
            "Machine Learning/AI": [
                "model", "training", "algorithm", "data", "feature", "prediction",
                "accuracy", "loss", "gradient", "neural", "network", "deep",
                "learning", "classification", "regression", "overfitting"
            ],
            "System Design": [
                "architecture", "scalability", "database", "cache", "load",
                "balance", "microservice", "api", "latency", "throughput",
                "availability", "consistency", "partition", "distributed"
            ],
            "Data Structures & Algorithms": [
                "complexity", "algorithm", "sorting", "searching", "tree",
                "graph", "hash", "array", "linked", "stack", "queue",
                "recursion", "dynamic", "programming", "big-o"
            ]
        }
        return keywords.get(topic, ["technical", "solution", "approach", "example"])
    
    def _extract_knowledge_insights(self, answer: str, topic: str,
                                   evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract knowledge insights for learning"""
        return {
            "topics_mentioned": self._extract_topics_mentioned(answer, topic),
            "depth_indicator": "deep" if evaluation.get("understanding_depth", 0) > 0.7 else "surface",
            "practical_focus": evaluation.get("practical_application", 0) > 0.6
        }
    
    def _extract_topics_mentioned(self, answer: str, topic: str) -> List[str]:
        """Extract specific topics mentioned in answer"""
        keywords = self._get_topic_keywords(topic)
        mentioned = [kw for kw in keywords if kw.lower() in answer.lower()]
        return mentioned[:5]  # Top 5
    
    def _analyze_progression(self, session: InterviewSession) -> str:
        """Analyze candidate's progression through interview"""
        if len(session.performance_history) < 2:
            return "insufficient_data"
        
        first_half = session.performance_history[:len(session.performance_history)//2]
        second_half = session.performance_history[len(session.performance_history)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 1:
            return "improving"
        elif second_avg < first_avg - 1:
            return "declining"
        return "consistent"
    
    def _update_session_metrics(self, session: InterviewSession, duration: float):
        """Update metrics after session"""
        n = self.interview_metrics["sessions_conducted"]
        current_avg = self.interview_metrics["avg_session_duration"]
        self.interview_metrics["avg_session_duration"] = (
            (current_avg * (n - 1) + duration) / n
        )
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a session"""
        if session_id not in self.active_sessions:
            return {"status": "not_found"}
        
        session = self.active_sessions[session_id]
        return {
            "status": "completed" if session.interview_complete else "in_progress",
            "phase": session.phase.value,
            "question_number": session.question_number,
            "candidate_state": session.candidate_state.value,
            "avg_score": sum(session.performance_history) / len(session.performance_history) if session.performance_history else 0
        }
    
    def get_interviewer_stats(self) -> Dict[str, Any]:
        """Get interviewer statistics"""
        return {
            "interview_metrics": self.interview_metrics,
            "reasoning_metrics": self.reasoning_engine.get_performance_report(),
            "personality": self.personality,
            "active_sessions": len(self.active_sessions)
        }
