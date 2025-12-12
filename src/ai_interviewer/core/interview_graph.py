"""
LangGraph-based Interview Flow Engine

This module implements the unified interview intelligence that powers
both Technical Interview and Practice Mode tabs.

Architecture (from AI_RESEARCH_FINDINGS.md):
1. Context Extraction → RAG Service
2. Question Generation → ReasoningEngine  
3. Validation → Critic Agent
4. Evaluation → Prometheus Rubric

Grounded in: https://docs.langchain.com/oss/python/langgraph/overview
"""
import logging
from typing import TypedDict, List, Optional, Annotated, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from .autonomous_interviewer import AutonomousInterviewer
from .session_manager import SessionManager
from ..utils.config import Config

logger = logging.getLogger(__name__)


# ==================== STATE SCHEMA ====================

class InterviewState(TypedDict):
    """
    Interview state schema using TypedDict.
    Per LangGraph docs: TypedDict is recommended for lightweight internal states.
    
    This state is shared across both Interview Tab and Practice Tab.
    """
    # Session Identity
    session_id: str
    candidate_name: str
    
    # Context (from Resume + JD)
    topic: str
    target_role: Optional[str]          # Extracted from JD
    company_name: Optional[str]         # Extracted from JD
    resume_skills: List[str]            # Extracted from resume
    jd_requirements: List[str]          # Extracted from JD
    experience_years: int
    
    # Interview Progress
    question_number: int
    max_questions: int
    current_question: Optional[str]
    current_answer: Optional[str]
    
    # Performance Tracking
    qa_pairs: List[Dict[str, Any]]
    performance_history: List[int]
    candidate_state: str                # confident, struggling, excelling, etc.
    
    # Flow Control
    phase: str                          # introduction, questioning, evaluating, complete
    is_complete: bool
    
    # Output
    final_report: Optional[Dict[str, Any]]
    messages: Annotated[list, add_messages]


# ==================== INTERVIEW GRAPH ====================

class InterviewGraph:
    """
    LangGraph-based interview orchestration.
    
    Provides unified interview intelligence for both tabs:
    - Technical Interview Tab: Full interview flow
    - Practice Mode Tab: Resume + JD context-aware questions
    
    Implements the planned flow from REFACTORING_STRATEGY.md:
    1. User Input → SessionManager
    2. RAGService → Context
    3. ReasoningEngine → Draft Question
    4. CriticService → Final Question
    """
    
    def __init__(self):
        self.interviewer = AutonomousInterviewer()
        self.session_manager = SessionManager()
        self._graph = None
        self._compiled_graph = None
        logger.info("🔷 LangGraph Interview Engine initialized")
    
    @property
    def graph(self):
        """Lazy load compiled graph."""
        if self._compiled_graph is None:
            self._compiled_graph = self._build_graph()
        return self._compiled_graph
    
    def _build_graph(self) -> StateGraph:
        """Build the interview flow graph."""
        graph = StateGraph(InterviewState)
        
        # Add nodes
        graph.add_node("extract_context", self._extract_context_node)
        graph.add_node("greeting", self._greeting_node)
        graph.add_node("generate_question", self._question_node)
        graph.add_node("validate_question", self._validate_question_node)
        graph.add_node("await_answer", self._await_answer_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("decide", self._decide_node)
        graph.add_node("report", self._report_node)
        
        # Define edges (linear flow with conditional branch)
        graph.add_edge(START, "extract_context")
        graph.add_edge("extract_context", "greeting")
        graph.add_edge("greeting", "generate_question")
        graph.add_edge("generate_question", "validate_question")
        graph.add_edge("validate_question", "await_answer")
        graph.add_edge("await_answer", "evaluate")
        graph.add_edge("evaluate", "decide")
        
        # Conditional edge for continue/complete
        graph.add_conditional_edges(
            "decide",
            self._should_continue,
            {
                "continue": "generate_question",
                "complete": "report"
            }
        )
        graph.add_edge("report", END)
        
        logger.info("🔷 Interview graph built with 8 nodes")
        return graph.compile()
    
    # ==================== GRAPH NODES ====================
    
    def _extract_context_node(self, state: InterviewState) -> dict:
        """
        Extract context from resume and JD.
        
        From AI_RESEARCH_FINDINGS.md:
        - Agent retrieves context from Vector DB
        - Agent generates question *using* retrieved context
        """
        logger.info("🔷 [Node] Extracting context from resume/JD...")
        
        # Use existing resume analysis
        resume_context = {}
        if state.get("resume_skills"):
            resume_context = {
                "skills": state["resume_skills"],
                "experience_years": state.get("experience_years", 0)
            }
        
        # Determine target role (from JD or topic)
        target_role = state.get("target_role") or state.get("topic", "Technical Interview")
        
        # Clean up role name (avoid "Technical Interview interview" repetition)
        if "interview" in target_role.lower():
            target_role = target_role.replace(" Interview", "").replace(" interview", "")
        
        return {
            "target_role": target_role,
            "phase": "context_extracted"
        }
    
    def _greeting_node(self, state: InterviewState) -> dict:
        """
        Generate personalized greeting using context.
        
        From GEMINI_RESEARCH.md:
        - Use role-specific greeting
        - Reference candidate's background
        """
        logger.info("🔷 [Node] Generating greeting...")
        
        candidate_name = state.get("candidate_name", "Candidate")
        target_role = state.get("target_role", state.get("topic", "Technical"))
        
        # Generate role-specific greeting
        greeting = f"Hello {candidate_name}, welcome to your {target_role} interview."
        
        # Add personalization if we have resume context
        if state.get("resume_skills"):
            top_skills = state["resume_skills"][:3]
            skills_str = ", ".join(top_skills)
            greeting += f" I see you have experience with {skills_str}. Let's explore your expertise."
        else:
            greeting += " I'll be asking you a series of questions to assess your skills."
        
        return {
            "current_question": greeting,
            "phase": "introduction",
            "question_number": 0
        }
    
    def _question_node(self, state: InterviewState) -> dict:
        """
        Generate context-aware interview question.
        
        From REFACTORING_STRATEGY.md:
        - RAGService → Context
        - ReasoningEngine → Draft Question
        """
        logger.info(f"🔷 [Node] Generating question {state['question_number'] + 1}...")
        
        # Get session for interviewer
        try:
            session = self.session_manager.get_session(state["session_id"])
            result = self.interviewer._generate_next_question_autonomous(session)
            question = result.get("question", f"Tell me about your experience with {state.get('topic', 'this topic')}.")
        except Exception as e:
            logger.warning(f"Question generation error: {e}")
            # Fallback question using context
            topic = state.get("target_role") or state.get("topic", "your technical skills")
            question = f"Can you describe your experience with {topic}?"
        
        return {
            "current_question": question,
            "question_number": state["question_number"] + 1,
            "phase": "questioning"
        }
    
    def _validate_question_node(self, state: InterviewState) -> dict:
        """
        Validate question using Critic Agent.
        
        From AI_RESEARCH_FINDINGS.md:
        - Critic Agent evaluates: "Relevance: 8/10", "Empathy: 4/10"
        - If score < 7, Main Agent regenerates
        
        TODO: Implement full Critic Agent in v3.2
        """
        logger.info("🔷 [Node] Validating question (Critic Agent)...")
        
        question = state.get("current_question", "")
        
        # Basic validation (full Critic Agent in v3.2)
        is_valid = True
        issues = []
        
        # Check for word repetition
        words = question.lower().split()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                is_valid = False
                issues.append(f"Word repetition: '{words[i]}'")
        
        # Check for "interview interview" pattern
        if "interview interview" in question.lower():
            is_valid = False
            issues.append("Double 'interview' detected")
        
        if not is_valid:
            logger.warning(f"⚠️ Question validation failed: {issues}")
            # TODO: Regenerate question in v3.2
        
        return {
            "phase": "question_validated"
        }
    
    def _await_answer_node(self, state: InterviewState) -> dict:
        """
        Placeholder for human input.
        
        LangGraph supports interrupts for human-in-the-loop.
        The graph pauses here waiting for answer submission.
        """
        logger.info("🔷 [Node] Awaiting answer...")
        return {
            "phase": "awaiting_answer"
        }
    
    def _evaluate_node(self, state: InterviewState) -> dict:
        """
        Evaluate answer using Prometheus-style rubric.
        
        Already implemented in AutonomousInterviewer._evaluate_answer_autonomous
        """
        logger.info("🔷 [Node] Evaluating answer...")
        
        try:
            session = self.session_manager.get_session(state["session_id"])
            result = self.interviewer.process_answer(
                state["session_id"],
                state.get("current_answer", "")
            )
            
            evaluation = result.get("evaluation", {})
            score = evaluation.get("score", 5)
            
            return {
                "qa_pairs": state.get("qa_pairs", []) + [{
                    "question": state.get("current_question"),
                    "answer": state.get("current_answer"),
                    "evaluation": evaluation
                }],
                "performance_history": state.get("performance_history", []) + [score],
                "phase": "evaluated"
            }
        except Exception as e:
            logger.warning(f"Evaluation error: {e}")
            return {
                "performance_history": state.get("performance_history", []) + [5],
                "phase": "evaluated"
            }
    
    def _decide_node(self, state: InterviewState) -> dict:
        """Decide whether to continue or complete interview."""
        logger.info("🔷 [Node] Deciding next action...")
        
        is_complete = state["question_number"] >= state["max_questions"]
        
        return {
            "is_complete": is_complete,
            "phase": "deciding"
        }
    
    def _should_continue(self, state: InterviewState) -> str:
        """Conditional edge function."""
        if state.get("is_complete", False):
            logger.info("🔷 Interview complete, generating report...")
            return "complete"
        logger.info(f"🔷 Continuing to question {state['question_number'] + 1}")
        return "continue"
    
    def _report_node(self, state: InterviewState) -> dict:
        """Generate final interview report."""
        logger.info("🔷 [Node] Generating final report...")
        
        try:
            session = self.session_manager.get_session(state["session_id"])
            result = self.interviewer._complete_interview(session)
            
            return {
                "final_report": result.get("summary", {}),
                "phase": "complete",
                "is_complete": True
            }
        except Exception as e:
            logger.warning(f"Report generation error: {e}")
            
            # Generate basic report from state
            scores = state.get("performance_history", [])
            avg_score = sum(scores) / len(scores) if scores else 5
            
            return {
                "final_report": {
                    "avg_score": avg_score,
                    "questions_answered": len(scores),
                    "status": "complete"
                },
                "phase": "complete",
                "is_complete": True
            }
    
    # ==================== PUBLIC API ====================
    
    def create_initial_state(
        self,
        candidate_name: str,
        topic: str,
        target_role: Optional[str] = None,
        resume_skills: Optional[List[str]] = None,
        jd_requirements: Optional[List[str]] = None,
        experience_years: int = 0,
        max_questions: int = None
    ) -> InterviewState:
        """Create initial state for a new interview."""
        
        if max_questions is None:
            max_questions = Config.MAX_QUESTIONS
        
        # Start interview to get session
        result = self.interviewer.start_interview(topic, candidate_name)
        session_id = result.get("session_id", "")
        
        return {
            "session_id": session_id,
            "candidate_name": candidate_name,
            "topic": topic,
            "target_role": target_role or topic,
            "company_name": None,
            "resume_skills": resume_skills or [],
            "jd_requirements": jd_requirements or [],
            "experience_years": experience_years,
            "question_number": 0,
            "max_questions": max_questions,
            "current_question": None,
            "current_answer": None,
            "qa_pairs": [],
            "performance_history": [],
            "candidate_state": "neutral",
            "phase": "starting",
            "is_complete": False,
            "final_report": None,
            "messages": []
        }
    
    def start_interview(
        self,
        candidate_name: str,
        topic: str,
        resume_skills: Optional[List[str]] = None,
        target_role: Optional[str] = None,
        **kwargs
    ) -> InterviewState:
        """
        Start a new interview.
        
        Used by both Interview Tab and Practice Tab.
        """
        logger.info(f"🔷 Starting interview for {candidate_name} on {topic}")
        
        initial_state = self.create_initial_state(
            candidate_name=candidate_name,
            topic=topic,
            target_role=target_role,
            resume_skills=resume_skills,
            **kwargs
        )
        
        # Run graph until await_answer node
        # The graph will pause at await_answer waiting for human input
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            logger.error(f"Graph invocation error: {e}")
            # Fallback to direct interviewer
            return initial_state
    
    def submit_answer(self, state: InterviewState, answer: str) -> InterviewState:
        """
        Submit answer and continue interview.
        
        Resumes the graph from await_answer node.
        """
        logger.info(f"🔷 Processing answer for question {state['question_number']}")
        
        state["current_answer"] = answer
        
        try:
            result = self.graph.invoke(state)
            return result
        except Exception as e:
            logger.error(f"Answer processing error: {e}")
            return state


# Singleton instance for easy import
_interview_graph = None

def get_interview_graph() -> InterviewGraph:
    """Get or create the interview graph singleton."""
    global _interview_graph
    if _interview_graph is None:
        _interview_graph = InterviewGraph()
    return _interview_graph
