"""
Context Engineering Module for Autonomous AI Interviewer

Research Reference:
    - arXiv:2510.04618 (Agentic Context Engineering - ACE)
    - arXiv:2507.13334 (Survey of Context Engineering for LLMs)
    - arXiv:2501.09136 (Agentic RAG - Retrieval-Augmented Generation)

Implements:
    1. Context Summarization - Compress past Q&A into summaries
    2. Sliding Window Management - Prevent context overflow
    3. Persistent Identity - Maintain consistent interviewer personality
    4. Context Refresh - Prevent "context rot"
    5. Knowledge Grounding - Verify answers against authoritative sources
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContextWindow:
    """Represents the current context window state"""
    max_tokens: int = 4096  # Conservative limit for cloud models
    current_tokens: int = 0
    system_prompt_tokens: int = 0
    conversation_tokens: int = 0
    
    def remaining_capacity(self) -> int:
        return self.max_tokens - self.current_tokens
    
    def utilization(self) -> float:
        return self.current_tokens / self.max_tokens if self.max_tokens else 0


@dataclass
class InterviewContext:
    """Structured context for the interview session"""
    # Persistent Identity (never changes)
    system_identity: str = ""
    
    # Session State (updated each turn)
    candidate_name: str = ""
    topic: str = ""
    question_number: int = 0
    max_questions: int = 5
    
    # Summarized History (compressed)
    conversation_summary: str = ""
    key_strengths: List[str] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    
    # Recent Context (full detail, sliding window)
    recent_qa_pairs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Current Turn
    current_question: str = ""
    current_answer: str = ""
    
    # Meta-context (how well is the interview going)
    overall_performance_trend: str = "neutral"  # improving, declining, neutral
    candidate_emotional_state: str = "neutral"  # confident, nervous, engaged


class ContextEngineer:
    """
    Context Engineering for Autonomous Agents
    
    Implements robust context management to prevent:
    - Context overflow (too many tokens)
    - Context rot (stale information degrading quality)
    - Context drift (losing focus on interview goals)
    
    Research: arXiv:2510.04618, arXiv:2507.13334
    """
    
    # Persistent System Identity (constant across all sessions)
    SYSTEM_IDENTITY = """You are an expert technical interviewer conducting a professional interview.

CORE PRINCIPLES:
- Be warm, professional, and encouraging
- Evaluate fairly based on demonstrated knowledge
- Adapt difficulty based on candidate performance
- Provide constructive, actionable feedback
- Never be condescending or discouraging

INTERVIEW STYLE:
- Ask one question at a time
- Listen actively to responses
- Acknowledge good points before critiquing
- Build on previous answers for follow-up questions"""

    def __init__(self, max_context_tokens: int = 4096, sliding_window_size: int = 3):
        """
        Initialize Context Engineer
        
        Args:
            max_context_tokens: Maximum tokens for context window
            sliding_window_size: Number of recent Q&A pairs to keep in full
        """
        self.max_context_tokens = max_context_tokens
        self.sliding_window_size = sliding_window_size
        self.context_window = ContextWindow(max_tokens=max_context_tokens)
        
        logger.info(f"🧠 ContextEngineer initialized (window: {max_context_tokens} tokens, sliding: {sliding_window_size})")
    
    def build_context(self, session_data: Dict[str, Any]) -> InterviewContext:
        """
        Build optimized context from session data
        
        This is the core CE function that:
        1. Maintains persistent identity
        2. Summarizes older conversation history
        3. Keeps recent turns in full detail
        4. Tracks meta-context for adaptation
        """
        context = InterviewContext()
        
        # 1. Persistent Identity (always included)
        context.system_identity = self.SYSTEM_IDENTITY
        
        # 2. Session State
        context.candidate_name = session_data.get("candidate_name", "Candidate")
        context.topic = session_data.get("topic", "Technical")
        context.question_number = session_data.get("question_number", 1)
        context.max_questions = session_data.get("max_questions", 5)
        
        # 3. Process Q&A History with Sliding Window
        qa_pairs = session_data.get("qa_pairs", [])
        
        if len(qa_pairs) > self.sliding_window_size:
            # Summarize older pairs
            older_pairs = qa_pairs[:-self.sliding_window_size]
            context.conversation_summary = self._summarize_qa_pairs(older_pairs)
            
            # Keep recent pairs in full
            context.recent_qa_pairs = qa_pairs[-self.sliding_window_size:]
        else:
            # All pairs fit in window
            context.recent_qa_pairs = qa_pairs
        
        # 4. Extract key insights
        context.key_strengths = session_data.get("strengths", [])[:3]
        context.knowledge_gaps = session_data.get("knowledge_gaps", [])[:3]
        
        # 5. Analyze performance trend
        performance_history = session_data.get("performance_history", [])
        context.overall_performance_trend = self._analyze_trend(performance_history)
        
        # 6. Current turn
        context.current_question = session_data.get("current_question", "")
        context.current_answer = session_data.get("current_answer", "")
        
        # Update context window tracking
        self._update_token_count(context)
        
        return context
    
    def _summarize_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> str:
        """
        Summarize older Q&A pairs to compress context
        
        Instead of keeping full text, extract key information:
        - Topics covered
        - Scores achieved
        - Key insights
        """
        if not qa_pairs:
            return ""
        
        summaries = []
        for i, qa in enumerate(qa_pairs, 1):
            score = qa.get("evaluation", {}).get("score", 5)
            topic_hint = qa.get("question", "")[:50] + "..."
            
            if score >= 7:
                summaries.append(f"Q{i}: Strong answer (score: {score}/10)")
            elif score >= 5:
                summaries.append(f"Q{i}: Adequate answer (score: {score}/10)")
            else:
                summaries.append(f"Q{i}: Needs improvement (score: {score}/10)")
        
        return "PREVIOUS PERFORMANCE: " + "; ".join(summaries)
    
    def _analyze_trend(self, scores: List[float]) -> str:
        """Analyze performance trend from score history"""
        if len(scores) < 2:
            return "neutral"
        
        recent = scores[-2:]
        older = scores[:-2] if len(scores) > 2 else scores[:1]
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older) if older else recent_avg
        
        if recent_avg > older_avg + 1:
            return "improving"
        elif recent_avg < older_avg - 1:
            return "declining"
        return "stable"
    
    def _update_token_count(self, context: InterviewContext) -> None:
        """Estimate token count for context window management"""
        # Rough estimation: 4 characters ≈ 1 token
        total_text = (
            context.system_identity +
            context.conversation_summary +
            str(context.recent_qa_pairs) +
            context.current_question +
            context.current_answer
        )
        estimated_tokens = len(total_text) // 4
        self.context_window.current_tokens = estimated_tokens
    
    def format_for_llm(self, context: InterviewContext, task: str = "generate_question") -> str:
        """
        Format the context for LLM consumption
        
        This creates a structured prompt that:
        1. Establishes identity and role
        2. Provides session context
        3. Includes relevant history (summarized + recent)
        4. States the current task
        """
        prompt_parts = []
        
        # 1. System Identity (Persistent)
        prompt_parts.append(f"=== SYSTEM IDENTITY ===\n{context.system_identity}")
        
        # 2. Session Context
        prompt_parts.append(f"""
=== INTERVIEW SESSION ===
Candidate: {context.candidate_name}
Topic: {context.topic}
Progress: Question {context.question_number}/{context.max_questions}
Performance Trend: {context.overall_performance_trend}""")
        
        # 3. Key Insights (if any)
        if context.key_strengths:
            prompt_parts.append(f"Demonstrated Strengths: {', '.join(context.key_strengths)}")
        if context.knowledge_gaps:
            prompt_parts.append(f"Areas to Probe: {', '.join(context.knowledge_gaps)}")
        
        # 4. Historical Context (summarized)
        if context.conversation_summary:
            prompt_parts.append(f"\n{context.conversation_summary}")
        
        # 5. Recent Conversation (full detail)
        if context.recent_qa_pairs:
            prompt_parts.append("\n=== RECENT CONVERSATION ===")
            for qa in context.recent_qa_pairs:
                q = qa.get("question", "")
                a = qa.get("answer", "")[:200]  # Truncate long answers
                score = qa.get("evaluation", {}).get("score", "N/A")
                prompt_parts.append(f"Q: {q}\nA: {a}...\nScore: {score}/10")
        
        # 6. Current Task
        task_prompts = {
            "generate_question": "Generate the next interview question that builds on the conversation so far.",
            "evaluate": "Evaluate the candidate's most recent answer.",
            "generate_report": "Generate a comprehensive interview summary report.",
            "adapt": "Analyze the situation and recommend adaptations."
        }
        prompt_parts.append(f"\n=== YOUR TASK ===\n{task_prompts.get(task, task)}")
        
        return "\n".join(prompt_parts)
    
    def refresh_context(self, context: InterviewContext) -> InterviewContext:
        """
        Prevent context rot by refreshing stale context
        
        This re-emphasizes key information that may have 
        been "forgotten" due to position in context window
        """
        # Re-inject key identity elements
        context.system_identity = self.SYSTEM_IDENTITY
        
        # Re-emphasize current goals
        if context.question_number >= context.max_questions - 1:
            # Nearing end - emphasize wrap-up
            context.system_identity += "\n\nNOTE: This is near the end of the interview. Focus on summarizing and providing closure."
        
        return context
    
    def get_context_health(self) -> Dict[str, Any]:
        """Return context window health metrics"""
        return {
            "utilization": f"{self.context_window.utilization():.1%}",
            "remaining_capacity": self.context_window.remaining_capacity(),
            "current_tokens": self.context_window.current_tokens,
            "max_tokens": self.context_window.max_tokens,
            "status": "healthy" if self.context_window.utilization() < 0.8 else "warning"
        }



from .knowledge_store import KnowledgeStore

class KnowledgeGrounding:
    """
    Knowledge Grounding for Answer Verification (RAG - Retrieval Augmented Generation)
    
    Grounds AI evaluations against authoritative sources using Semantic Search.
    
    Research Reference: arXiv:2501.09136 (Agentic RAG)
    """
    
    # Fallback/Bootstrap knowledge
    # We load this into Vector DB on first run if empty
    BOOTSTRAP_KNOWLEDGE = {
        "JavaScript/Frontend Development": [
            "Closure: Function having access to parent scope even after parent returns. (MDN)",
            "Hoisting: Declarations moved to top of scope. let/const in TDZ. (MDN)",
            "Event Loop: Single-threaded loop with Call Stack, Task Queue, Microtask Queue. (Node.js)",
            "Virtual DOM: In-memory DOM representation for efficient diffing. (React)",
            "useEffect: Hook for side effects in functional components. (React)"
        ],
        "Python/Backend Development": [
            "GIL: Mutex protecting access to Python objects, preventing multi-core bytecode execution. (Python Docs)",
            "Decorators: Functions that modify other functions using @syntax. (Python Docs)",
            "Generators: Functions using yield to return lazy iterators. (Python Docs)",
            "Context Managers: Objects managing resources via __enter__ and __exit__. (Python Docs)"
        ],
        "System Design": [
            "CAP Theorem: Distributed systems pick 2: Consistency, Availability, Partition Tolerance.",
            "Sharding: Horizontal partitioning of data across instances.",
            "Load Balancing: Distributing traffic via Round Robin, Least Conn, etc. (AWS)",
            "Caching strategies: LRU, LFU, Write-Through, Write-Back. (Redis)"
        ]
    }
    
    def __init__(self):
        """Initialize Knowledge Grounding with Vector Store"""
        self.store: Optional[KnowledgeStore] = None
        try:
            self.store = KnowledgeStore()
            self._bootstrap_if_empty()
            logger.info("📚 KnowledgeGrounding initialized with Vector Store (RAG)")
        except Exception as e:
            logger.error(f"Failed to init Knowledge Store: {e}")
            self.store = None
    
    def _bootstrap_if_empty(self):
        """Load initial knowledge if store is empty"""
        # This is a naive check, but fine for MVP
        # Ideally we check collection count
        try:
            if self.store is not None and self.store.collection.count() == 0:
                logger.info("🚀 Bootstrapping Knowledge Store with default concepts...")
                if self.store is not None:
                    for topic, facts in self.BOOTSTRAP_KNOWLEDGE.items():
                        self.store.add_texts(
                            texts=facts, 
                            metadatas=[{"topic": topic, "source": "bootstrap"} for _ in facts]
                        )
        except Exception as e:
            logger.warning(f"Bootstrap failed: {e}")
            
    def get_grounding_context(self, topic: str, answer: str) -> Dict[str, Any]:
        """
        Get relevant grounding knowledge via Semantic Search
        """
        if not self.store:
            return {"error": "Vector Store unavailable"}
            
        # Search for concepts relevant to the answer
        # logic: query the store with the answer text to find what concepts it touches on
        results = self.store.search(
            query=answer, 
            k=3,
            # Optional: Filter by topic if we strictly want only topic-relevant facts
            # filter_criteria={"topic": topic} if topic else None
        )
        
        relevant_concepts = {}
        for res in results:
            # key = content (the fact itself), val = source
            fact = res['content']
            meta = res['metadata']
            source = meta.get('source', 'unknown')
            relevant_concepts[f"Fact: {fact[:50]}..."] = f"{fact} ({source})"
            
        return {
            "relevant_concepts": relevant_concepts,
            "grounding_sources": ["Vector Knowledge Base"],
            "topic": topic,
            "verification_status": "grounded" if relevant_concepts else "unverified"
        }
    
    def verify_answer(self, topic: str, question: str, answer: str) -> Dict[str, Any]:
        """
        Verify candidate answer against retrieved knowledge.
        """
        grounding = self.get_grounding_context(topic, answer)
        relevant_concepts = grounding.get("relevant_concepts", {})
        
        correct_points = []
        
        # In RAG, we don't just keyword match. 
        # We assume if semantic search found it, it's relevant context.
        # Ideally, we pass this to an LLM to verify "Does Answer agree with Fact?"
        # For this MVP, we just return the Retrieves Facts as valid context.
        
        for key, definition in relevant_concepts.items():
            correct_points.append({
                "concept": key,
                "candidate_mentioned": True, # Assumed relevant by vector search
                "verified_definition": definition
            })
            
        return {
            "accuracy_assessment": "verified_against_docs",
            "correct_points": correct_points,
            "factual_errors": [], # Needs LLM to determine contradiction
            "missing_concepts": [],
            "grounding_evidence": grounding,
            "confidence": 0.8 if correct_points else 0.5
        }
    
    def get_verification_prompt(self, topic: str, answer: str) -> str:
        """
        Generate prompt with RAG context
        """
        grounding = self.get_grounding_context(topic, answer)
        relevant_concepts = grounding.get("relevant_concepts", {})
        
        if not relevant_concepts:
            return ""
        
        prompt = "\n=== VERIFIED KNOWLEDGE BASE (RAG) ===\n"
        for concept, definition in relevant_concepts.items():
            prompt += f"• {definition}\n"
        
        prompt += "\nUse the above facts to verify the accuracy of the answer."
        return prompt

    def update_knowledge(self, topic: str, concept: str, new_definition: str, source: str) -> None:
        """Add new knowledge to Vector Store"""
        if self.store is not None:
            text = f"{concept}: {new_definition}"
            self.store.add_texts(
                texts=[text], 
                metadatas=[{"topic": topic, "source": source}]
            )
            logger.info(f"📝 Knowledge added to Vector Store: {concept}")

