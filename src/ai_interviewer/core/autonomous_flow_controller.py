"""
Autonomous Flow Controller
Integrates the Autonomous Interviewer with the application

This provides the main entry point for the autonomous interview system.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue

from ..utils.config import Config
from ..utils.types import (
    InterviewStartResponse,
    AnswerProcessResponse,
    ResumeAnalysisResponse,
    SessionStatusResponse,
    SystemStatusResponse
)
from ..exceptions import (
    SessionError,
    LLMError,
    ResourceError,
    ProcessingError
)
from ..utils.error_handler import ErrorHandler
from .autonomous_interviewer import AutonomousInterviewer, InterviewSession

logger = logging.getLogger(__name__)


class AutonomousFlowController:
    """
    Autonomous Flow Controller with Self-Thinking AI
    
    This controller manages:
    - Session lifecycle with autonomous decision-making
    - Concurrent interview handling
    - Performance monitoring and self-optimization
    - Graceful error recovery
    """
    
    def __init__(self, max_concurrent_sessions: int = 20, model_name: Optional[str] = None, **kwargs):
        if model_name is None:
            model_name = Config.DEFAULT_MODEL
        self.interviewer = AutonomousInterviewer(model_name)
        self.max_concurrent_sessions = max_concurrent_sessions
        self.session_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_sessions)
        
        # Performance tracking
        self.metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "avg_response_time": 0.0,
            "autonomous_decisions": 0,
            "self_recoveries": 0
        }
        
        logger.info(f"🤖 Autonomous Flow Controller initialized (max sessions: {max_concurrent_sessions})")
    
    def start_interview(self, topic: str, candidate_name: str, custom_context: Optional[Dict[str, Any]] = None) -> InterviewStartResponse:
        """Start interview with autonomous AI interviewer"""
        try:
            # Check concurrency
            active_count = len(self.interviewer.session_manager.active_sessions)
            if active_count >= self.max_concurrent_sessions:
                return {
                    "status": "error",
                    "message": "Maximum sessions reached. Please retry later.",
                    "error_code": "CONCURRENCY_LIMIT"
                }
            
            # Start autonomous interview with optional custom context
            result = self.interviewer.start_interview(topic, candidate_name, custom_context=custom_context)
            
            if result["status"] == "started":
                with self.session_lock:
                    self.metrics["total_sessions"] += 1
                    self.metrics["active_sessions"] = len(self.interviewer.session_manager.active_sessions)
                
                logger.info(f"🎤 Autonomous interview started: {result['session_id']}")
            
            # Convert to InterviewStartResponse format
            response: InterviewStartResponse = {
                "status": result.get("status", "error"),
                "session_id": result.get("session_id", ""),
                "greeting": result.get("greeting", ""),
                "first_question": result.get("first_question", ""),
                "message": result.get("message")
            }
            return response
            
        except (SessionError, LLMError, ResourceError) as e:
            ErrorHandler.log_error(e, {"operation": "start_interview", "topic": topic})
            with self.session_lock:
                self.metrics["self_recoveries"] += 1
            error_response = ErrorHandler.from_exception(e, {"operation": "start_interview"})
            return {
                "status": "error",
                **error_response
            }
        except Exception as e:
            ErrorHandler.log_error(e, {"operation": "start_interview", "topic": topic})
            with self.session_lock:
                self.metrics["self_recoveries"] += 1
            error_response = ErrorHandler.from_exception(e, {"operation": "start_interview"})
            return {
                "status": "error",
                **error_response
            }
    
    def process_answer(self, session_id: str, answer: str) -> AnswerProcessResponse:
        """Process answer with autonomous reasoning"""
        try:
            start_time = time.time()
            
            result = self.interviewer.process_answer(session_id, answer)
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time)
            
            if result["status"] in ["continue", "completed"]:
                with self.session_lock:
                    self.metrics["autonomous_decisions"] += 1
                    self.metrics["active_sessions"] = len(self.interviewer.session_manager.active_sessions)
            
            # Convert to AnswerProcessResponse format
            response: AnswerProcessResponse = {
                "status": result.get("status", "error"),
                "next_question": result.get("next_question"),
                "question_number": result.get("question_number", 0),
                "evaluation": result.get("evaluation"),
                "feedback": result.get("feedback"),
                "reasoning": result.get("reasoning"),
                "final_report": result.get("final_report"),
                "summary": result.get("summary"),
                "message": result.get("message")
            }
            return response
            
        except (SessionError, LLMError, ProcessingError) as e:
            ErrorHandler.log_error(e, {"operation": "process_answer", "session_id": session_id})
            with self.session_lock:
                self.metrics["self_recoveries"] += 1
            error_response = ErrorHandler.from_exception(e, {"operation": "process_answer", "session_id": session_id})
            return {
                "status": "error",
                "evaluation": {"score": 0},
                "feedback": "System error occurred.",
                **error_response
            }
        except Exception as e:
            ErrorHandler.log_error(e, {"operation": "process_answer", "session_id": session_id})
            with self.session_lock:
                self.metrics["self_recoveries"] += 1
            error_response = ErrorHandler.from_exception(e, {"operation": "process_answer", "session_id": session_id})
            return {
                "status": "error",
                "evaluation": {"score": 0},
                "feedback": "System error occurred.",
                **error_response
            }

    def analyze_resume(self, resume_text: str) -> ResumeAnalysisResponse:
        """Delegate resume analysis to interviewer"""
        result = self.interviewer.analyze_resume(resume_text)
        # Convert to ResumeAnalysisResponse format
        response: ResumeAnalysisResponse = {
            "skills": result.get("skills", []),
            "experience_level": result.get("experience_level", "junior"),
            "detected_role": result.get("detected_role"),
            "suggested_topics": result.get("suggested_topics", []),
            "key_qualifications": result.get("key_qualifications", []),
            "summary": result.get("summary", ""),
            "experience_years": result.get("experience_years", 0)
        }
        return response

    
    def _update_metrics(self, processing_time: float):
        """Update performance metrics"""
        alpha = 0.1
        with self.session_lock:
            self.metrics["avg_response_time"] = (
                (1 - alpha) * self.metrics["avg_response_time"] + 
                alpha * processing_time
            )
    
    def get_session_status(self, session_id: str) -> SessionStatusResponse:
        """Get status of a specific session"""
        return self.interviewer.get_session_status(session_id)  # type: ignore[return-value]
    
    def get_system_status(self) -> SystemStatusResponse:
        """Get comprehensive system status"""
        interviewer_stats = self.interviewer.get_interviewer_stats()
        
        return {
            "status": "operational",
            "autonomous_features": {
                "self_thinking": True,
                "logical_reasoning": True,
                "self_resilient": True,
                "human_like_conduct": True,
                "adaptive_behavior": True
            },
            "performance": self.metrics,
            "interviewer_stats": interviewer_stats,
            "capacity": len(self.interviewer.session_manager.active_sessions)
        }
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get learning and analytics data"""
        return {
            "session_metrics": self.metrics,
            "reasoning_metrics": self.interviewer.reasoning_engine.get_performance_report(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        if self.metrics["avg_response_time"] > 3.0:
            recommendations.append("Response time above target - consider optimization")
        
        utilization = len(self.interviewer.session_manager.active_sessions) / self.max_concurrent_sessions
        if utilization > 0.8:
            recommendations.append("High capacity utilization - consider scaling")
        
        if self.metrics["self_recoveries"] > 5:
            recommendations.append("Multiple error recoveries - review system stability")
        
        return recommendations or ["System operating normally"]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired = []
        
        for session_id, session in list(self.interviewer.session_manager.active_sessions.items()):
            if current_time - session.start_time > 3600:  # 1 hour timeout
                expired.append(session_id)
        
        for session_id in expired:
            self.interviewer.session_manager.delete_session(session_id)
            logger.info(f"Cleaned up expired session: {session_id}")
        
        if expired:
            with self.session_lock:
                self.metrics["active_sessions"] = len(self.interviewer.session_manager.active_sessions)
    
    def shutdown(self):
        """Shutdown the controller"""
        logger.info("Shutting down Autonomous Flow Controller...")
        self.executor.shutdown(wait=True)
        self.interviewer.session_manager.active_sessions.clear()
        logger.info("Shutdown complete")
    
    def __del__(self):
        try:
            self.shutdown()
        except Exception as e:
            # Swallowing exceptions in __del__ is necessary but we log it
            logger.debug(f"Shutdown cleanup: {e}")
