"""
Session management module for AI Interviewer
Handles session state, validation, and cleanup
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import uuid
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class InterviewStatus(Enum):
    """Interview session status"""
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    EXPIRED = "expired"

dataclass
class QAPair:
    """Question and Answer pair with evaluation"""
    question: str
    answer: str
    evaluation: Dict
    timestamp: datetime = field(default_factory=datetime.utcnow)

dataclass
class InterviewSession:
    """Interview session data"""
    session_id: str
    topic: str
    candidate_name: str
    status: InterviewStatus
    start_time: datetime
    last_activity: datetime
    question_count: int = 1
    max_questions: int = 5
    current_question: Optional[str] = None
    qa_pairs: List[QAPair] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if session has expired (1 hour timeout)"""
        return (datetime.utcnow() - self.last_activity) > timedelta(hours=1)

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

class SessionManager:
    """Manages interview sessions with thread safety"""  
    
    # Valid interview topics
    VALID_TOPICS = {
        "JavaScript/Frontend Development",
        "Python/Backend Development",
        "Machine Learning/AI",
        "System Design",
        "Data Structures & Algorithms"
    }

    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}
        self._lock = threading.Lock()

    def create_session(self, topic: str, candidate_name: str) -> Tuple[bool, str, Optional[str]]:
        """Create new interview session with validation
        Returns: (success, message, session_id)"""
        # Validate inputs
        if not self._validate_topic(topic):
            return False, "Invalid topic selected", None
        
        if not self._validate_name(candidate_name):
            return False, "Invalid name (must be 1-100 characters)", None

        session_id = str(uuid.uuid4())
        
        with self._lock:
            # Create new session
            session = InterviewSession(
                session_id=session_id,
                topic=topic,
                candidate_name=candidate_name,
                status=InterviewStatus.READY,
                start_time=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            self._sessions[session_id] = session
            
        logger.info(f"Created new session {session_id} for {candidate_name}")
        return True, "Session created successfully", session_id

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID and update activity timestamp""" 
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                if session.is_expired:
                    self.cleanup_session(session_id)
                    return None
                session.update_activity()
            return session

    def cleanup_session(self, session_id: str):
        """Clean up session data""" 
        with self._lock:
            if session_id in self._sessions:
                logger.info(f"Cleaning up session {session_id}")
                del self._sessions[session_id]

    def cleanup_expired(self):
        """Clean up all expired sessions""" 
        with self._lock:
            expired = [
                session_id for session_id, session in self._sessions.items()
                if session.is_expired
            ]
            for session_id in expired:
                self.cleanup_session(session_id)
            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")

    @staticmethod
    def _validate_topic(topic: str) -> bool:
        """Validate interview topic""" 
        return topic in SessionManager.VALID_TOPICS

    @staticmethod
    def _validate_name(name: str) -> bool:
        """Validate candidate name""" 
        return bool(name and name.strip() and len(name.strip()) <= 100)