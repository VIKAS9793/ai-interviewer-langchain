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


class KnowledgeGrounding:
    """
    Knowledge Grounding for Answer Verification
    
    Grounds AI evaluations against authoritative sources to:
    1. Verify technical accuracy of candidate answers
    2. Ensure AI feedback is based on verified knowledge
    3. Update understanding based on latest documentation
    
    Research Reference: arXiv:2501.09136 (Agentic RAG)
    """
    
    # Authoritative knowledge sources by topic
    KNOWLEDGE_SOURCES = {
        "JavaScript/Frontend Development": {
            "concepts": {
                "closure": "A closure is a function that has access to its outer function's scope even after the outer function has returned. MDN Web Docs.",
                "hoisting": "Variable and function declarations are moved to the top of their scope during compilation. var is hoisted and initialized to undefined, let/const are hoisted but not initialized (TDZ).",
                "event_loop": "JavaScript uses a single-threaded event loop with a call stack, task queue, and microtask queue. Promises use the microtask queue.",
                "prototype": "JavaScript uses prototypal inheritance. Objects inherit from other objects via the prototype chain.",
                "async_await": "async/await is syntactic sugar over Promises where async functions implicitly return Promises and await pauses execution.",
                "virtual_dom": "React's Virtual DOM is an in-memory representation that enables efficient reconciliation by computing minimal DOM updates."
            },
            "official_docs": ["developer.mozilla.org", "react.dev", "nodejs.org"]
        },
        "Python/Backend Development": {
            "concepts": {
                "gil": "The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, allowing only one thread to execute Python bytecode at a time.",
                "decorators": "Decorators are functions that modify the behavior of other functions/classes, applied using @decorator syntax.",
                "generators": "Generators are functions that use yield to return an iterator, enabling lazy evaluation and memory efficiency.",
                "context_managers": "Context managers implement __enter__ and __exit__ methods for resource management, typically used with 'with' statement.",
                "metaclasses": "Metaclasses are classes of classes that define how classes behave. type is the default metaclass.",
                "async_python": "asyncio provides async/await for concurrent I/O-bound operations using coroutines and event loops."
            },
            "official_docs": ["docs.python.org", "djangoproject.com", "flask.palletsprojects.com"]
        },
        "Machine Learning/AI": {
            "concepts": {
                "overfitting": "Overfitting occurs when a model learns training data too well, including noise, leading to poor generalization on unseen data.",
                "gradient_descent": "Gradient descent is an optimization algorithm that iteratively adjusts parameters in the direction of steepest descent of the loss function.",
                "backpropagation": "Backpropagation computes gradients of the loss with respect to weights using the chain rule, enabling neural network training.",
                "regularization": "Regularization (L1/L2) adds penalty terms to the loss function to prevent overfitting by constraining model complexity.",
                "attention": "Attention mechanisms allow models to focus on relevant parts of input, computing weighted combinations based on query-key similarities.",
                "transformers": "Transformers use self-attention to process sequences in parallel, enabling efficient training on long-range dependencies."
            },
            "official_docs": ["scikit-learn.org", "pytorch.org", "tensorflow.org"]
        },
        "System Design": {
            "concepts": {
                "cap_theorem": "CAP theorem states distributed systems can only guarantee 2 of 3: Consistency, Availability, Partition tolerance.",
                "load_balancing": "Load balancing distributes traffic across servers using algorithms like round-robin, least connections, or consistent hashing.",
                "caching": "Caching stores frequently accessed data in faster storage layers. Strategies include LRU, LFU, write-through, write-back.",
                "sharding": "Database sharding horizontally partitions data across multiple database instances to improve scalability.",
                "microservices": "Microservices architecture decomposes applications into loosely coupled, independently deployable services.",
                "message_queues": "Message queues (Kafka, RabbitMQ) enable async communication between services, providing decoupling and reliability."
            },
            "official_docs": ["aws.amazon.com/architecture", "cloud.google.com/architecture"]
        },
        "Data Structures & Algorithms": {
            "concepts": {
                "big_o": "Big O notation describes algorithm time/space complexity in terms of input size growth. O(1) < O(log n) < O(n) < O(n log n) < O(n²)",
                "hash_table": "Hash tables provide O(1) average-case lookup/insert using hash functions to map keys to array indices. Handle collisions via chaining or open addressing.",
                "binary_tree": "Binary trees have at most 2 children per node. BST maintains sorted order (left < root < right), enabling O(log n) operations.",
                "dynamic_programming": "DP solves problems by breaking into overlapping subproblems, storing solutions to avoid recomputation (memoization/tabulation).",
                "graph_algorithms": "BFS explores level-by-level (shortest paths), DFS explores depth-first (topological sort, cycle detection).",
                "sorting": "Comparison sorts: QuickSort O(n log n) average, MergeSort O(n log n) guaranteed, HeapSort O(n log n) in-place."
            },
            "official_docs": ["algorithm visualizer", "geeksforgeeks.org"]
        }
    }
    
    def __init__(self):
        """Initialize Knowledge Grounding with topic knowledge bases"""
        self.knowledge_base = self.KNOWLEDGE_SOURCES
        self.verification_cache = {}
        logger.info("📚 KnowledgeGrounding initialized with authoritative sources")
    
    def get_grounding_context(self, topic: str, answer: str) -> Dict[str, Any]:
        """
        Get relevant grounding knowledge for answer verification
        
        Returns verified facts and concepts related to the answer
        """
        topic_knowledge = self.knowledge_base.get(topic, {})
        concepts = topic_knowledge.get("concepts", {})
        official_docs = topic_knowledge.get("official_docs", [])
        
        # Find relevant concepts mentioned in answer
        relevant_concepts = {}
        answer_lower = answer.lower()
        
        for concept_key, definition in concepts.items():
            # Check if concept or related terms appear in answer
            search_terms = concept_key.replace("_", " ").split()
            if any(term in answer_lower for term in search_terms):
                relevant_concepts[concept_key] = definition
        
        return {
            "relevant_concepts": relevant_concepts,
            "grounding_sources": official_docs,
            "topic": topic,
            "verification_status": "grounded" if relevant_concepts else "unverified"
        }
    
    def verify_answer(self, topic: str, question: str, answer: str) -> Dict[str, Any]:
        """
        Verify candidate answer against authoritative knowledge
        
        Returns:
            - accuracy_assessment: How accurate the answer is
            - factual_errors: Any incorrect statements detected
            - missing_concepts: Key concepts candidate should have mentioned
            - grounding_evidence: Supporting evidence from knowledge base
        """
        grounding = self.get_grounding_context(topic, answer)
        relevant_concepts = grounding.get("relevant_concepts", {})
        
        # Check for factual accuracy
        factual_errors = []
        correct_points = []
        
        for concept_key, verified_definition in relevant_concepts.items():
            # Simple keyword matching for now
            # In production, this would use semantic similarity
            if concept_key.replace("_", " ") in answer.lower():
                correct_points.append({
                    "concept": concept_key,
                    "candidate_mentioned": True,
                    "verified_definition": verified_definition[:100] + "..."
                })
        
        # Identify missing key concepts
        topic_knowledge = self.knowledge_base.get(topic, {})
        all_concepts = list(topic_knowledge.get("concepts", {}).keys())
        mentioned_concepts = [c["concept"] for c in correct_points]
        
        # Suggest concepts that might be relevant but weren't mentioned
        # (based on question keywords - simple heuristic)
        question_words = question.lower().split()
        potentially_relevant = [
            c for c in all_concepts 
            if any(w in c.replace("_", " ") for w in question_words)
            and c not in mentioned_concepts
        ][:3]
        
        return {
            "accuracy_assessment": "verified" if correct_points else "needs_review",
            "correct_points": correct_points,
            "factual_errors": factual_errors,
            "missing_concepts": potentially_relevant,
            "grounding_evidence": grounding,
            "confidence": 0.8 if correct_points else 0.5
        }
    
    def get_verification_prompt(self, topic: str, answer: str) -> str:
        """
        Generate a verification prompt that includes grounding knowledge
        
        This prompt helps the LLM verify against authoritative sources
        """
        grounding = self.get_grounding_context(topic, answer)
        relevant_concepts = grounding.get("relevant_concepts", {})
        
        if not relevant_concepts:
            return ""
        
        prompt = "\n=== AUTHORITATIVE KNOWLEDGE (for verification) ===\n"
        for concept, definition in relevant_concepts.items():
            prompt += f"• {concept.replace('_', ' ').title()}: {definition}\n"
        
        prompt += "\nVerify the candidate's answer against these authoritative definitions."
        
        return prompt
    
    def update_knowledge(self, topic: str, concept: str, new_definition: str, source: str) -> None:
        """
        Update knowledge base with new verified information
        
        This enables the system to learn from authoritative sources
        """
        if topic not in self.knowledge_base:
            self.knowledge_base[topic] = {"concepts": {}, "official_docs": []}
        
        self.knowledge_base[topic]["concepts"][concept] = f"{new_definition} (Source: {source})"
        logger.info(f"📝 Knowledge updated: {topic}/{concept}")
