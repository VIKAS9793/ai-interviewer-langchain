
import time
import logging
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from .autonomous_reasoning_engine import CandidateState, ThoughtChain

try:
    from ..utils.config import Config
except ImportError:
    # Fallback for testing
    class _FallbackConfig:
        SESSION_EXPIRATION_SECONDS = 3600
        SESSION_CLEANUP_INTERVAL_SECONDS = 300
    Config = _FallbackConfig  # type: ignore[assignment]

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
    last_activity: float = field(default_factory=time.time)  # Track last activity for expiration
    interview_complete: bool = False
    final_report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)  # Stores custom_context for resume/JD
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if self.interview_complete:
            return False  # Completed sessions don't expire
        elapsed = time.time() - self.last_activity
        return elapsed > Config.SESSION_EXPIRATION_SECONDS


class SessionManager:
    """
    Manages interview session state with expiration and cleanup.
    Responsible for CRUD operations on InterviewSession objects.
    
    Security Features:
    - Session expiration (prevents memory leaks)
    - Automatic cleanup of expired sessions
    - Thread-safe operations
    """
    def __init__(self):
        self.active_sessions: Dict[str, InterviewSession] = {}
        self._lock = threading.Lock()  # Thread safety
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()
        logger.info("💾 SessionManager initialized with expiration support")
    
    def _start_cleanup_thread(self):
        """Start background thread for session cleanup"""
        def cleanup_loop():
            while not self._stop_cleanup.is_set():
                self._stop_cleanup.wait(Config.SESSION_CLEANUP_INTERVAL_SECONDS)
                if not self._stop_cleanup.is_set():
                    self.cleanup_expired_sessions()
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("🧹 Session cleanup thread started")
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            expired_ids = [
                session_id for session_id, session in self.active_sessions.items()
                if session.is_expired()
            ]
            
            for session_id in expired_ids:
                del self.active_sessions[session_id]
                logger.info(f"🗑️ Expired session removed: {session_id}")
            
            if expired_ids:
                logger.info(f"🧹 Cleaned up {len(expired_ids)} expired session(s)")
            
            return len(expired_ids)
    
    def shutdown(self):
        """Stop cleanup thread (for graceful shutdown)"""
        self._stop_cleanup.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("💾 SessionManager shutdown complete")

    def create_session(self, session_id: str, candidate_name: str, topic: str, max_questions: int = 5) -> InterviewSession:
        """Create and register a new session"""
        with self._lock:
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
        """
        Retrieve a session by ID.
        Returns None if session doesn't exist or is expired.
        """
        with self._lock:
            session = self.active_sessions.get(session_id)
            if session and session.is_expired():
                # Remove expired session
                del self.active_sessions[session_id]
                logger.info(f"🗑️ Expired session accessed and removed: {session_id}")
                return None
            if session:
                session.update_activity()  # Update activity on access
            return session

    def list_active_sessions(self) -> List[str]:
        """List all active (non-expired) session IDs"""
        with self._lock:
            # Filter out expired sessions
            active = [
                session_id for session_id, session in self.active_sessions.items()
                if not session.is_expired()
            ]
            return active
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self._lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"🗑️ Session deleted: {session_id}")
                return True
            return False

    def save_session(self, session: InterviewSession):
        """
        Persist session state.
        Currently in-memory, but abstraction helps future DB integration.
        Updates activity timestamp.
        """
        with self._lock:
            session.update_activity()
            self.active_sessions[session.session_id] = session
