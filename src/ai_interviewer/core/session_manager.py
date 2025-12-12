
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from .autonomous_reasoning_engine import CandidateState, ThoughtChain

logger = logging.getLogger(__name__)

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
    metadata: Dict[str, Any] = field(default_factory=dict)  # Stores custom_context for resume/JD


class SessionManager:
    """
    Manages interview session state.
    Responsible for CRUD operations on InterviewSession objects.
    """
    def __init__(self):
        self.active_sessions: Dict[str, InterviewSession] = {}
        logger.info("💾 SessionManager initialized")

    def create_session(self, session_id: str, candidate_name: str, topic: str, max_questions: int = 5) -> InterviewSession:
        """Create and register a new session"""
        session = InterviewSession(
            session_id=session_id,
            candidate_name=candidate_name,
            topic=topic,
            max_questions=max_questions
        )
        self.active_sessions[session_id] = session
        logger.info(f"🆕 Session created: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve a session by ID"""
        return self.active_sessions.get(session_id)

    def list_active_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self.active_sessions.keys())
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"🗑️ Session deleted: {session_id}")
            return True
        return False

    def save_session(self, session: InterviewSession):
        """
        Persist session state.
        Currently in-memory, but abstraction helps future DB integration.
        """
        self.active_sessions[session.session_id] = session
