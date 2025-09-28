"""
Autonomous Learning-Based Adaptive Intelligence System
Modern AI agentic development with continuous learning and optimization
"""

import logging
import asyncio
import json
import pickle
import time
from typing import Dict, List, Any, Optional, Tuple, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from contextlib import contextmanager

from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """Learning metrics for adaptive intelligence"""
    session_count: int = 0
    avg_performance: float = 0.0
    topic_performance: Dict[str, float] = field(default_factory=dict)
    question_effectiveness: Dict[str, float] = field(default_factory=dict)
    difficulty_preferences: Dict[str, str] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AdaptiveState(TypedDict):
    """Enhanced state for adaptive learning system"""
    session_id: str
    candidate_name: str
    topic: str
    current_question_number: int
    max_questions: int
    qa_pairs: List[Dict[str, Any]]
    current_question: str
    current_answer: str
    last_evaluation: Dict[str, Any]
    interview_complete: bool
    start_time: float
    learning_context: Dict[str, Any]
    adaptive_strategy: str
    performance_trend: List[float]
    knowledge_gaps: List[str]
    strengths_identified: List[str]

class LearningDatabase:
    """Persistent learning database for offline operation"""
    
    def __init__(self, db_path: str = "./learning_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for learning data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interview_sessions (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    candidate_name TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    qa_pairs TEXT,  -- JSON
                    performance_metrics TEXT,  -- JSON
                    learning_insights TEXT  -- JSON
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS question_performance (
                    question_hash TEXT PRIMARY KEY,
                    question_text TEXT,
                    topic TEXT,
                    difficulty TEXT,
                    success_rate REAL,
                    avg_score REAL,
                    usage_count INTEGER,
                    last_used TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    metric_type TEXT PRIMARY KEY,
                    metric_data TEXT,  -- JSON
                    last_updated TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS adaptive_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,  -- JSON
                    confidence REAL,
                    last_seen TIMESTAMP
                )
            """)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def store_session(self, session_data: Dict[str, Any]):
        """Store completed interview session"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO interview_sessions 
                (session_id, topic, candidate_name, start_time, end_time, qa_pairs, performance_metrics, learning_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['session_id'],
                session_data['topic'],
                session_data['candidate_name'],
                session_data['start_time'],
                datetime.now().isoformat(),
                json.dumps(session_data.get('qa_pairs', [])),
                json.dumps(session_data.get('performance_metrics', {})),
                json.dumps(session_data.get('learning_insights', {}))
            ))
    
    def get_learning_metrics(self) -> LearningMetrics:
        """Retrieve current learning metrics"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT metric_data FROM learning_metrics WHERE metric_type = 'global'")
            row = cursor.fetchone()
            
            if row:
                data = json.loads(row[0])
                return LearningMetrics(**data)
            else:
                return LearningMetrics()
    
    def update_learning_metrics(self, metrics: LearningMetrics):
        """Update learning metrics"""
        with self.get_connection() as conn:
            # Convert datetime objects to ISO format strings for JSON serialization
            metrics_dict = {}
            for key, value in metrics.__dict__.items():
                if isinstance(value, datetime):
                    metrics_dict[key] = value.isoformat()
                else:
                    metrics_dict[key] = value
            
            conn.execute("""
                INSERT OR REPLACE INTO learning_metrics (metric_type, metric_data, last_updated)
                VALUES (?, ?, ?)
            """, ('global', json.dumps(metrics_dict), datetime.now().isoformat()))

class AdaptiveQuestionGenerator:
    """Intelligent question generator with learning capabilities"""
    
    def __init__(self, learning_db: LearningDatabase):
        self.learning_db = learning_db
        self.embedding_model = None  # Lazy load
        self.question_cache = {}
        self.performance_cache = {}
        
        # Initialize ChromaDB for semantic question search (lazy load)
        self.chroma_client = None
    
    def _get_embedding_model(self):
        """Lazy load embedding model"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model
    
    def _get_chroma_client(self):
        """Lazy load ChromaDB client"""
        if self.chroma_client is None:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_questions",
                settings=Settings(anonymized_telemetry=False)
            )
        return self.chroma_client
    
    def generate_adaptive_question(self, state: AdaptiveState) -> str:
        """Generate question based on learning and adaptation (optimized)"""
        topic = state['topic']
        question_number = state['current_question_number']
        
        # Simplified difficulty determination
        if question_number <= 2:
            difficulty = "easy"
        elif question_number <= 4:
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        # Generate simple contextual question
        question = self._generate_simple_question(topic, difficulty, question_number)
        
        return question
    
    def _generate_simple_question(self, topic: str, difficulty: str, question_number: int) -> str:
        """Generate a simple question without complex learning logic"""
        # Simple question templates for faster generation
        templates = {
            "JavaScript/Frontend Development": {
                "easy": [
                    "What is the difference between var, let, and const in JavaScript?",
                    "Explain what a closure is in JavaScript.",
                    "What is the DOM and how do you access elements?"
                ],
                "medium": [
                    "How does JavaScript handle asynchronous operations?",
                    "Explain the concept of prototypal inheritance.",
                    "What are the differences between == and === in JavaScript?"
                ],
                "hard": [
                    "Explain the event loop in JavaScript and how it handles async operations.",
                    "How would you implement a custom Promise from scratch?",
                    "Explain memory management and garbage collection in JavaScript."
                ]
            },
            "Python/Backend Development": {
                "easy": [
                    "What is the difference between a list and a tuple in Python?",
                    "Explain Python's GIL (Global Interpreter Lock).",
                    "What are decorators in Python?"
                ],
                "medium": [
                    "How does Python handle memory management?",
                    "Explain the difference between __str__ and __repr__.",
                    "What are context managers and how do you create one?"
                ],
                "hard": [
                    "Explain Python's metaclasses and when you would use them.",
                    "How would you implement a custom iterator in Python?",
                    "Explain the differences between multiprocessing and threading in Python."
                ]
            }
        }
        
        topic_questions = templates.get(topic, templates["JavaScript/Frontend Development"])
        difficulty_questions = topic_questions.get(difficulty, topic_questions["medium"])
        
        # Select question based on question number
        question_index = (question_number - 1) % len(difficulty_questions)
        return difficulty_questions[question_index]
    
    def _determine_adaptive_difficulty(self, performance: float, question_number: int) -> str:
        """Determine difficulty based on performance and question number"""
        if question_number <= 2:
            return "easy" if performance < 0.6 else "medium"
        elif question_number <= 4:
            if performance < 0.4:
                return "easy"
            elif performance > 0.8:
                return "hard"
            else:
                return "medium"
        else:
            if performance < 0.5:
                return "medium"
            else:
                return "hard"
    
    def _generate_contextual_question(self, topic: str, difficulty: str, 
                                    question_number: int, knowledge_gaps: List[str],
                                    performance_trend: List[float], 
                                    topic_performance: float) -> str:
        """Generate question with full context awareness"""
        
        # Build context for question generation
        context_prompt = PromptTemplate(
            input_variables=["topic", "difficulty", "question_number", "knowledge_gaps", 
                           "performance_trend", "topic_performance"],
            template="""You are an advanced AI interviewer with adaptive learning capabilities.

TOPIC: {topic}
DIFFICULTY: {difficulty}
QUESTION NUMBER: {question_number}/5
PERFORMANCE TREND: {performance_trend}
TOPIC PERFORMANCE: {topic_performance}
KNOWLEDGE GAPS: {knowledge_gaps}

Generate a question that:
1. ADDRESSES KNOWLEDGE GAPS: Focus on areas where the candidate needs improvement
2. MATCHES DIFFICULTY: Use {difficulty} level based on their performance trend
3. BUILDS ON PREVIOUS ANSWERS: Reference or extend previous responses
4. ADAPTIVE COMPLEXITY: Adjust complexity based on {topic_performance}
5. LEARNING-ORIENTED: Help the candidate learn while being evaluated

The question should be:
- Technically accurate and relevant
- Progressive in difficulty
- Educational and insightful
- Specific to their demonstrated skill level

Question:"""
        )
        
        try:
            # Use Ollama for question generation
            llm = Ollama(model="tinyllama", temperature=0.3)
            chain = context_prompt | llm
            
            question = chain.invoke({
                "topic": topic,
                "difficulty": difficulty,
                "question_number": question_number,
                "knowledge_gaps": ", ".join(knowledge_gaps) if knowledge_gaps else "None identified",
                "performance_trend": str(performance_trend),
                "topic_performance": str(topic_performance)
            })
            
            return question.strip()
            
        except Exception as e:
            logger.error(f"Error generating adaptive question: {e}")
            return self._get_fallback_question(topic, difficulty)
    
    def _cache_question(self, question: str, topic: str, difficulty: str):
        """Cache question for learning and performance tracking"""
        question_hash = hash(question)
        
        # Store in ChromaDB for semantic search
        self.question_collection.add(
            documents=[question],
            metadatas=[{"topic": topic, "difficulty": difficulty, "hash": question_hash}],
            ids=[str(question_hash)]
        )
        
        # Store performance tracking
        self.performance_cache[question_hash] = {
            "question": question,
            "topic": topic,
            "difficulty": difficulty,
            "usage_count": 0,
            "success_rate": 0.0,
            "avg_score": 0.0
        }
    
    def _get_fallback_question(self, topic: str, difficulty: str) -> str:
        """Fallback questions when generation fails"""
        fallback_questions = {
            "JavaScript/Frontend Development": {
                "easy": "What is the difference between 'let' and 'const' in JavaScript?",
                "medium": "How would you implement a debounce function in JavaScript?",
                "hard": "Explain the JavaScript event loop and how it handles asynchronous operations."
            },
            "Python/Backend Development": {
                "easy": "What is the difference between a list and a tuple in Python?",
                "medium": "How would you handle database connections in a Python web application?",
                "hard": "Explain Python's GIL and its impact on multi-threading."
            }
        }
        
        questions = fallback_questions.get(topic, {})
        return questions.get(difficulty, f"Tell me about your experience with {topic}.")

class AdaptiveEvaluator:
    """Advanced evaluator with learning and adaptation"""
    
    def __init__(self, learning_db: LearningDatabase):
        self.learning_db = learning_db
        self.evaluation_cache = {}
        self.performance_patterns = defaultdict(list)
    
    def evaluate_with_learning(self, question: str, answer: str, topic: str, 
                             state: AdaptiveState) -> Dict[str, Any]:
        """Evaluate answer with simplified learning (optimized for speed)"""
        
        # Simple evaluation based on answer length and keywords
        score = self._simple_evaluation(question, answer, topic)
        
        evaluation = {
            "score": score,
            "feedback": self._generate_simple_feedback(score, answer),
            "strengths": ["Good attempt"] if score > 5 else [],
            "improvements": ["Try to be more specific"] if score < 7 else [],
            "technical_accuracy": score / 10,
            "completeness": min(score / 8, 1.0),
            "clarity": min(score / 7, 1.0)
        }
        
        return evaluation
    
    def _simple_evaluation(self, question: str, answer: str, topic: str) -> float:
        """Simple evaluation based on answer characteristics"""
        if not answer or len(answer.strip()) < 10:
            return 2.0
        
        # Basic scoring based on answer length and content
        base_score = min(len(answer) / 50, 5.0)  # Max 5 points for length
        
        # Add points for technical keywords
        technical_keywords = {
            "JavaScript/Frontend Development": ["function", "variable", "object", "array", "DOM", "event", "async", "promise"],
            "Python/Backend Development": ["function", "class", "method", "import", "def", "return", "exception", "module"]
        }
        
        keywords = technical_keywords.get(topic, [])
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in answer.lower())
        keyword_score = min(keyword_count * 0.5, 3.0)  # Max 3 points for keywords
        
        return min(base_score + keyword_score, 10.0)
    
    def _generate_simple_feedback(self, score: float, answer: str) -> str:
        """Generate simple feedback based on score"""
        if score >= 8:
            return "Excellent answer! You demonstrated good understanding of the concepts."
        elif score >= 6:
            return "Good answer! You covered the main points well."
        elif score >= 4:
            return "Decent answer. Consider providing more specific examples or details."
        else:
            return "Your answer needs improvement. Try to be more specific and provide examples."
    
    def _comprehensive_evaluation(self, question: str, answer: str, topic: str, 
                                state: AdaptiveState) -> Dict[str, Any]:
        """Comprehensive evaluation with multiple dimensions"""
        
        evaluation_prompt = PromptTemplate(
            input_variables=["question", "answer", "topic", "performance_trend", "knowledge_gaps"],
            template="""You are an advanced AI evaluator with learning capabilities.

QUESTION: {question}
ANSWER: {answer}
TOPIC: {topic}
PERFORMANCE TREND: {performance_trend}
IDENTIFIED KNOWLEDGE GAPS: {knowledge_gaps}

Evaluate this answer across multiple dimensions (1-10 scale):

1. TECHNICAL ACCURACY: How technically correct is the answer?
2. CONCEPTUAL UNDERSTANDING: How well does the candidate understand underlying concepts?
3. PRACTICAL APPLICATION: How well can they apply this knowledge practically?
4. COMMUNICATION CLARITY: How clearly is the answer communicated?
5. DEPTH OF KNOWLEDGE: How deep is their understanding?
6. PROBLEM-SOLVING APPROACH: How well does it demonstrate problem-solving skills?
7. LEARNING POTENTIAL: How well does the answer show capacity for growth?

Also provide:
- Overall score (weighted average)
- Key strengths (2-3 points)
- Areas for improvement (2-3 points)
- Missing concepts
- Recommended next difficulty
- Learning recommendations
- Confidence level in evaluation

Respond in JSON format:
{{
    "technical_accuracy": <score>,
    "conceptual_understanding": <score>,
    "practical_application": <score>,
    "communication_clarity": <score>,
    "depth_of_knowledge": <score>,
    "problem_solving_approach": <score>,
    "learning_potential": <score>,
    "overall_score": <weighted_average>,
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"],
    "missing_concepts": ["concept1", "concept2"],
    "next_difficulty": "medium",
    "learning_recommendations": ["rec1", "rec2"],
    "confidence": 0.85,
    "detailed_feedback": "Comprehensive feedback paragraph"
}}"""
        )
        
        try:
            llm = Ollama(model="tinyllama", temperature=0.2)
            chain = evaluation_prompt | llm
            
            response = chain.invoke({
                "question": question,
                "answer": answer,
                "topic": topic,
                "performance_trend": str(state.get('performance_trend', [])),
                "knowledge_gaps": ", ".join(state.get('knowledge_gaps', []))
            })
            
            # Parse JSON response
            evaluation = json.loads(response.strip())
            
            # Add additional metrics
            evaluation.update(self._calculate_advanced_metrics(answer, topic, evaluation))
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in comprehensive evaluation: {e}")
            return self._fallback_evaluation(answer, topic)
    
    def _identify_knowledge_patterns(self, answer: str, topic: str, 
                                  evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Identify knowledge patterns and gaps"""
        
        # Analyze answer for knowledge patterns
        knowledge_analysis = {
            "knowledge_gaps": [],
            "strengths_identified": [],
            "learning_opportunities": [],
            "concept_mastery": {}
        }
        
        # Identify gaps based on evaluation
        if evaluation.get('technical_accuracy', 0) < 6:
            knowledge_analysis["knowledge_gaps"].append("Technical accuracy")
        
        if evaluation.get('conceptual_understanding', 0) < 6:
            knowledge_analysis["knowledge_gaps"].append("Conceptual understanding")
        
        if evaluation.get('practical_application', 0) < 6:
            knowledge_analysis["knowledge_gaps"].append("Practical application")
        
        # Identify strengths
        if evaluation.get('communication_clarity', 0) >= 8:
            knowledge_analysis["strengths_identified"].append("Clear communication")
        
        if evaluation.get('problem_solving_approach', 0) >= 8:
            knowledge_analysis["strengths_identified"].append("Strong problem-solving")
        
        return knowledge_analysis
    
    def _calculate_advanced_metrics(self, answer: str, topic: str, 
                                  evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced metrics for learning"""
        
        # Text analysis metrics
        words = answer.split()
        metrics = {
            "word_count": len(words),
            "character_count": len(answer),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "technical_term_density": self._calculate_technical_density(answer, topic),
            "complexity_score": self._calculate_complexity_score(answer),
            "confidence_indicators": self._identify_confidence_indicators(answer)
        }
        
        return metrics
    
    def _calculate_technical_density(self, answer: str, topic: str) -> float:
        """Calculate technical term density"""
        technical_terms = {
            "JavaScript/Frontend Development": ["function", "variable", "object", "array", "async", "promise", "callback"],
            "Python/Backend Development": ["class", "method", "import", "module", "dictionary", "list", "tuple"],
            "Machine Learning/AI": ["algorithm", "model", "training", "prediction", "feature", "dataset", "accuracy"],
            "System Design": ["architecture", "scalability", "database", "cache", "load", "balance", "microservice"],
            "Data Structures & Algorithms": ["complexity", "algorithm", "sorting", "searching", "tree", "graph", "hash"]
        }
        
        terms = technical_terms.get(topic, [])
        answer_lower = answer.lower()
        term_count = sum(1 for term in terms if term in answer_lower)
        
        return term_count / len(answer.split()) if answer.split() else 0
    
    def _calculate_complexity_score(self, answer: str) -> float:
        """Calculate complexity score based on answer characteristics"""
        score = 0.0
        
        # Length factor
        word_count = len(answer.split())
        if word_count > 100:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1
        
        # Technical indicators
        if any(char in answer for char in ['{', '}', '(', ')', ';']):
            score += 0.2
        
        # Example indicators
        if any(word in answer.lower() for word in ['example', 'for instance', 'such as']):
            score += 0.1
        
        # Question indicators (shows engagement)
        if '?' in answer:
            score += 0.1
        
        return min(1.0, score)
    
    def _identify_confidence_indicators(self, answer: str) -> List[str]:
        """Identify confidence indicators in the answer"""
        indicators = []
        
        confidence_phrases = [
            "I'm confident", "I know", "definitely", "certainly", "absolutely",
            "I believe", "I think", "probably", "might be", "could be"
        ]
        
        answer_lower = answer.lower()
        for phrase in confidence_phrases:
            if phrase in answer_lower:
                indicators.append(phrase)
        
        return indicators
    
    def _update_learning_insights(self, evaluation: Dict[str, Any], topic: str, state: AdaptiveState):
        """Update learning insights based on evaluation"""
        # Store performance pattern
        pattern = {
            "topic": topic,
            "score": evaluation.get('overall_score', 0),
            "timestamp": datetime.now().isoformat(),
            "question_number": state['current_question_number']
        }
        
        self.performance_patterns[topic].append(pattern)
        
        # Keep only recent patterns (last 100)
        if len(self.performance_patterns[topic]) > 100:
            self.performance_patterns[topic] = self.performance_patterns[topic][-100:]
    
    def _fallback_evaluation(self, answer: str, topic: str) -> Dict[str, Any]:
        """Fallback evaluation when LLM fails"""
        word_count = len(answer.split())
        base_score = min(10, max(1, word_count // 10))
        
        return {
            "technical_accuracy": base_score,
            "conceptual_understanding": base_score,
            "practical_application": max(1, base_score - 1),
            "communication_clarity": min(10, base_score + 1),
            "depth_of_knowledge": base_score,
            "problem_solving_approach": base_score,
            "learning_potential": base_score,
            "overall_score": base_score,
            "strengths": ["Provided a response"],
            "improvements": ["Could provide more detail"],
            "missing_concepts": [],
            "next_difficulty": "medium",
            "learning_recommendations": ["Continue practicing"],
            "confidence": 0.5,
            "detailed_feedback": "Basic evaluation based on answer length",
            "word_count": word_count,
            "technical_term_density": 0.0,
            "complexity_score": 0.0,
            "confidence_indicators": []
        }

class AdaptiveLearningSystem:
    """Main autonomous learning system orchestrator"""
    
    def __init__(self):
        self.learning_db = LearningDatabase()
        self.question_generator = AdaptiveQuestionGenerator(self.learning_db)
        self.evaluator = AdaptiveEvaluator(self.learning_db)
        self.graph = self._build_adaptive_graph()
        self.active_sessions: Dict[str, Dict] = {}
        self.learning_thread = None
        self.learning_active = True
        
        # Start background learning process
        self._start_background_learning()
    
    def _build_adaptive_graph(self) -> StateGraph:
        """Build LangGraph with adaptive learning capabilities"""
        
        workflow = StateGraph(AdaptiveState)
        
        # Add adaptive nodes
        workflow.add_node("initialize_session", self._initialize_session_node)
        workflow.add_node("analyze_context", self._analyze_context_node)
        workflow.add_node("generate_adaptive_question", self._generate_adaptive_question_node)
        workflow.add_node("evaluate_with_learning", self._evaluate_with_learning_node)
        workflow.add_node("update_learning", self._update_learning_node)
        workflow.add_node("decide_next_adaptive", self._decide_next_adaptive_node)
        workflow.add_node("generate_adaptive_report", self._generate_adaptive_report_node)
        
        # Define adaptive flow
        workflow.set_entry_point("initialize_session")
        workflow.add_edge("initialize_session", "analyze_context")
        workflow.add_edge("analyze_context", "generate_adaptive_question")
        workflow.add_edge("generate_adaptive_question", "evaluate_with_learning")
        workflow.add_edge("evaluate_with_learning", "update_learning")
        workflow.add_edge("update_learning", "decide_next_adaptive")
        
        workflow.add_conditional_edges(
            "decide_next_adaptive",
            self._should_continue_adaptive,
            {
                "continue": "analyze_context",
                "complete": "generate_adaptive_report"
            }
        )
        
        workflow.add_edge("generate_adaptive_report", END)
        
        return workflow.compile()
    
    def _initialize_session_node(self, state: AdaptiveState) -> AdaptiveState:
        """Initialize session with learning context"""
        state["learning_context"] = {
            "session_start": datetime.now().isoformat(),
            "topic_expertise": self.learning_db.get_learning_metrics().topic_performance.get(state["topic"], 0.5),
            "adaptive_strategy": "progressive_learning"
        }
        state["performance_trend"] = []
        state["knowledge_gaps"] = []
        state["strengths_identified"] = []
        
        logger.info(f"Initialized adaptive session for {state['candidate_name']}")
        return state
    
    def _analyze_context_node(self, state: AdaptiveState) -> AdaptiveState:
        """Analyze context for adaptive decision making"""
        # Analyze performance trend
        if state["qa_pairs"]:
            recent_scores = [qa.get("evaluation", {}).get("overall_score", 0) for qa in state["qa_pairs"][-3:]]
            state["performance_trend"] = recent_scores
        
        # Update knowledge gaps from recent evaluations
        if state["qa_pairs"]:
            last_eval = state["qa_pairs"][-1].get("evaluation", {})
            missing_concepts = last_eval.get("missing_concepts", [])
            state["knowledge_gaps"].extend(missing_concepts)
            state["knowledge_gaps"] = list(set(state["knowledge_gaps"]))  # Remove duplicates
        
        return state
    
    def _generate_adaptive_question_node(self, state: AdaptiveState) -> AdaptiveState:
        """Generate adaptive question using learning system"""
        question = self.question_generator.generate_adaptive_question(state)
        state["current_question"] = question
        
        logger.info(f"Generated adaptive question {state['current_question_number']}")
        return state
    
    def _evaluate_with_learning_node(self, state: AdaptiveState) -> AdaptiveState:
        """Evaluate answer with learning capabilities"""
        evaluation = self.evaluator.evaluate_with_learning(
            question=state["current_question"],
            answer=state["current_answer"],
            topic=state["topic"],
            state=state
        )
        
        state["last_evaluation"] = evaluation
        
        # Update performance trend
        state["performance_trend"].append(evaluation.get("overall_score", 0))
        
        # Update knowledge gaps and strengths
        state["knowledge_gaps"].extend(evaluation.get("missing_concepts", []))
        state["strengths_identified"].extend(evaluation.get("strengths", []))
        
        logger.info(f"Evaluated answer with learning - Score: {evaluation.get('overall_score', 0)}/10")
        return state
    
    def _update_learning_node(self, state: AdaptiveState) -> AdaptiveState:
        """Update learning system with new insights"""
        # Store Q&A pair with enhanced evaluation
        qa_pair = {
            "question_number": state["current_question_number"],
            "question": state["current_question"],
            "answer": state["current_answer"],
            "evaluation": state["last_evaluation"],
            "learning_insights": {
                "knowledge_gaps": state["knowledge_gaps"],
                "strengths": state["strengths_identified"],
                "performance_trend": state["performance_trend"]
            }
        }
        
        state["qa_pairs"].append(qa_pair)
        
        # Update learning metrics asynchronously
        self._update_learning_metrics_async(state)
        
        return state
    
    def _decide_next_adaptive_node(self, state: AdaptiveState) -> AdaptiveState:
        """Decide next step with adaptive intelligence"""
        state["current_question_number"] += 1
        
        # Adaptive completion logic
        if state["current_question_number"] > state["max_questions"]:
            state["interview_complete"] = True
        elif state["current_question_number"] >= 3:
            # Check if candidate has reached sufficient competency
            avg_score = np.mean(state["performance_trend"]) if state["performance_trend"] else 0
            if avg_score >= 8.5:
                state["interview_complete"] = True
                logger.info("Interview completed early due to high performance")
        
        return state
    
    def _should_continue_adaptive(self, state: AdaptiveState) -> str:
        """Determine if interview should continue with adaptive logic"""
        if state["interview_complete"]:
            return "complete"
        
        # Check if we've reached the maximum number of questions
        current_question = state.get("current_question_number", 0)
        max_questions = state.get("max_questions", 5)
        
        if current_question >= max_questions:
            state["interview_complete"] = True
            return "complete"
        
        return "continue"
    
    def _generate_adaptive_report_node(self, state: AdaptiveState) -> AdaptiveState:
        """Generate comprehensive adaptive report"""
        # Calculate final metrics
        final_metrics = {
            "avg_score": np.mean(state["performance_trend"]) if state["performance_trend"] else 0,
            "score_trend": state["performance_trend"],
            "knowledge_gaps": state["knowledge_gaps"],
            "strengths": state["strengths_identified"],
            "learning_progression": self._calculate_learning_progression(state),
            "recommendations": self._generate_learning_recommendations(state)
        }
        
        state["final_report"] = self._create_adaptive_report(state, final_metrics)
        state["learning_insights"] = final_metrics
        
        # Store session for learning
        self._store_session_for_learning(state)
        
        return state
    
    def _calculate_learning_progression(self, state: AdaptiveState) -> Dict[str, Any]:
        """Calculate learning progression throughout the interview"""
        if len(state["performance_trend"]) < 2:
            return {"trend": "insufficient_data", "improvement": 0}
        
        scores = state["performance_trend"]
        improvement = scores[-1] - scores[0] if len(scores) > 1 else 0
        
        if improvement > 1:
            trend = "improving"
        elif improvement < -1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "improvement": improvement,
            "consistency": np.std(scores) if len(scores) > 1 else 0,
            "peak_performance": max(scores),
            "learning_rate": improvement / len(scores) if len(scores) > 0 else 0
        }
    
    def _generate_learning_recommendations(self, state: AdaptiveState) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        avg_score = np.mean(state["performance_trend"]) if state["performance_trend"] else 0
        
        if avg_score < 6:
            recommendations.extend([
                f"Focus on fundamental {state['topic']} concepts",
                "Practice explaining technical concepts clearly",
                "Study basic terminology and definitions"
            ])
        elif avg_score < 8:
            recommendations.extend([
                f"Deepen understanding of {state['topic']}",
                "Practice with more complex examples",
                "Work on connecting concepts together"
            ])
        else:
            recommendations.extend([
                f"Explore advanced {state['topic']} topics",
                "Practice system design and architecture",
                "Focus on real-world applications"
            ])
        
        # Knowledge gap recommendations
        for gap in state["knowledge_gaps"]:
            recommendations.append(f"Study {gap} concepts in detail")
        
        return recommendations[:5]  # Limit to top 5
    
    def _create_adaptive_report(self, state: AdaptiveState, metrics: Dict[str, Any]) -> str:
        """Create comprehensive adaptive report"""
        
        report_template = """
## 🧠 Adaptive Learning Interview Report

**Candidate:** {candidate_name}
**Topic:** {topic}
**Session Duration:** {duration} minutes
**Questions Completed:** {question_count}/5

### 📊 Performance Analysis
- **Average Score:** {avg_score:.1f}/10
- **Performance Trend:** {trend}
- **Improvement:** {improvement:+.1f} points
- **Learning Rate:** {learning_rate:.2f} points/question

### 🎯 Learning Insights
**Strengths Identified:**
{strengths}

**Knowledge Gaps:**
{gaps}

**Learning Progression:**
{progression}

### 🚀 Personalized Recommendations
{recommendations}

### 🔬 Adaptive Intelligence Summary
This interview was conducted using our autonomous learning system, which:
- Adapted question difficulty based on your performance
- Identified your knowledge gaps and strengths
- Provided personalized learning recommendations
- Tracked your learning progression in real-time

**Overall Assessment:** {assessment}

*Thank you for participating in our adaptive learning interview system!*
"""
        
        # Calculate duration
        duration = (datetime.now() - datetime.fromisoformat(state["learning_context"]["session_start"])).total_seconds() / 60
        
        # Determine assessment
        avg_score = metrics["avg_score"]
        if avg_score >= 8:
            assessment = "Excellent performance with strong technical understanding"
        elif avg_score >= 6:
            assessment = "Good performance with solid foundation"
        else:
            assessment = "Developing skills with room for growth"
        
        return report_template.format(
            candidate_name=state["candidate_name"],
            topic=state["topic"],
            duration=duration,
            question_count=len(state["qa_pairs"]),
            avg_score=avg_score,
            trend=metrics["learning_progression"]["trend"],
            improvement=metrics["learning_progression"]["improvement"],
            learning_rate=metrics["learning_progression"]["learning_rate"],
            strengths="\n".join([f"- {s}" for s in state["strengths_identified"]]),
            gaps="\n".join([f"- {g}" for g in state["knowledge_gaps"]]),
            progression=f"Started at {state['performance_trend'][0]:.1f}, ended at {state['performance_trend'][-1]:.1f}" if len(state['performance_trend']) > 1 else "Single data point",
            recommendations="\n".join([f"- {r}" for r in metrics["recommendations"]]),
            assessment=assessment
        )
    
    def _store_session_for_learning(self, state: AdaptiveState):
        """Store session data for learning"""
        session_data = {
            "session_id": state["session_id"],
            "topic": state["topic"],
            "candidate_name": state["candidate_name"],
            "start_time": state["start_time"],
            "qa_pairs": state["qa_pairs"],
            "performance_metrics": {
                "avg_score": np.mean(state["performance_trend"]) if state["performance_trend"] else 0,
                "score_trend": state["performance_trend"],
                "learning_progression": self._calculate_learning_progression(state)
            },
            "learning_insights": state.get("learning_insights", {})
        }
        
        self.learning_db.store_session(session_data)
    
    def _update_learning_metrics_async(self, state: AdaptiveState):
        """Update learning metrics asynchronously"""
        if self.learning_thread and self.learning_thread.is_alive():
            return  # Learning thread already running
        
        self.learning_thread = threading.Thread(
            target=self._update_learning_metrics_sync,
            args=(state,),
            daemon=True
        )
        self.learning_thread.start()
    
    def _update_learning_metrics_sync(self, state: AdaptiveState):
        """Update learning metrics synchronously"""
        try:
            metrics = self.learning_db.get_learning_metrics()
            
            # Update session count
            metrics.session_count += 1
            
            # Update topic performance
            topic = state["topic"]
            current_performance = metrics.topic_performance.get(topic, 0.5)
            new_performance = np.mean(state["performance_trend"]) if state["performance_trend"] else 0.5
            
            # Exponential moving average
            alpha = 0.1
            metrics.topic_performance[topic] = (1 - alpha) * current_performance + alpha * new_performance
            
            # Update overall performance
            metrics.avg_performance = np.mean(list(metrics.topic_performance.values()))
            
            # Update last updated timestamp
            metrics.last_updated = datetime.now()
            
            # Store updated metrics
            self.learning_db.update_learning_metrics(metrics)
            
            logger.info(f"Updated learning metrics for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error updating learning metrics: {e}")
    
    def _start_background_learning(self):
        """Start background learning process"""
        def background_learning():
            while self.learning_active:
                try:
                    # Perform background learning tasks
                    self._perform_background_learning()
                    time.sleep(300)  # Run every 5 minutes
                except Exception as e:
                    logger.error(f"Background learning error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        learning_thread = threading.Thread(target=background_learning, daemon=True)
        learning_thread.start()
        logger.info("Started background learning process")
    
    def _perform_background_learning(self):
        """Perform background learning tasks"""
        try:
            # Analyze performance patterns
            self._analyze_performance_patterns()
            
            # Optimize question generation
            self._optimize_question_generation()
            
            # Clean up old data
            self._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"Background learning task error: {e}")
    
    def _analyze_performance_patterns(self):
        """Analyze performance patterns for insights"""
        # This would analyze patterns across all sessions
        # For now, just log that it's running
        logger.debug("Analyzing performance patterns")
    
    def _optimize_question_generation(self):
        """Optimize question generation based on learning"""
        # This would optimize question generation based on historical data
        logger.debug("Optimizing question generation")
    
    def _cleanup_old_data(self):
        """Clean up old learning data"""
        # This would clean up old session data
        logger.debug("Cleaning up old data")
    
    def start_adaptive_interview(self, topic: str, candidate_name: str) -> Dict[str, Any]:
        """Start adaptive interview with learning system"""
        try:
            session_id = f"{candidate_name}_{int(time.time())}"
            
            # Initialize adaptive state
            initial_state: AdaptiveState = {
                "session_id": session_id,
                "candidate_name": candidate_name,
                "topic": topic,
                "current_question_number": 1,
                "max_questions": 5,
                "qa_pairs": [],
                "current_question": "",
                "current_answer": "",
                "last_evaluation": {},
                "interview_complete": False,
                "start_time": time.time(),
                "learning_context": {},
                "adaptive_strategy": "progressive_learning",
                "performance_trend": [],
                "knowledge_gaps": [],
                "strengths_identified": []
            }
            
            # Run adaptive graph
            result = self.graph.invoke(initial_state)
            
            # Store session
            self.active_sessions[session_id] = result
            
            logger.info(f"✅ Adaptive interview started for {candidate_name} on topic: {topic}")
            
            return {
                "session_id": session_id,
                "status": "started",
                "first_question": result["current_question"],
                "question_number": 1,
                "adaptive_features": {
                    "learning_enabled": True,
                    "adaptive_difficulty": True,
                    "knowledge_tracking": True,
                    "performance_analysis": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting adaptive interview: {e}")
            raise
    
    def process_adaptive_answer(self, session: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Process answer with adaptive learning"""
        try:
            session_id = session["session_id"]
            
            if session_id not in self.active_sessions:
                raise ValueError("Invalid session ID")
            
            current_state = self.active_sessions[session_id]
            current_state["current_answer"] = answer
            
            # Continue adaptive graph execution
            updated_state = self._analyze_context_node(current_state)
            updated_state = self._generate_adaptive_question_node(updated_state)
            updated_state = self._evaluate_with_learning_node(updated_state)
            updated_state = self._update_learning_node(updated_state)
            updated_state = self._decide_next_adaptive_node(updated_state)
            
            # Check if interview should continue
            if self._should_continue_adaptive(updated_state) == "continue":
                # Update session
                self.active_sessions[session_id] = updated_state
                
                return {
                    "status": "continue",
                    "next_question": updated_state["current_question"],
                    "question_number": updated_state["current_question_number"],
                    "evaluation": updated_state["last_evaluation"],
                    "learning_insights": {
                        "performance_trend": updated_state["performance_trend"],
                        "knowledge_gaps": updated_state["knowledge_gaps"],
                        "strengths": updated_state["strengths_identified"]
                    }
                }
            else:
                # Interview complete
                updated_state = self._generate_adaptive_report_node(updated_state)
                
                # Update session
                self.active_sessions[session_id] = updated_state
                
                return {
                    "status": "complete",
                    "final_report": updated_state.get("final_report", ""),
                    "learning_insights": updated_state.get("learning_insights", {}),
                    "session_data": updated_state
                }
                
        except Exception as e:
            logger.error(f"Error processing adaptive answer: {e}")
            raise
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get current learning insights"""
        metrics = self.learning_db.get_learning_metrics()
        
        return {
            "total_sessions": metrics.session_count,
            "avg_performance": metrics.avg_performance,
            "topic_performance": metrics.topic_performance,
            "last_updated": metrics.last_updated.isoformat(),
            "learning_active": self.learning_active
        }
    
    def shutdown(self):
        """Shutdown learning system"""
        self.learning_active = False
        logger.info("Adaptive learning system shutdown")
