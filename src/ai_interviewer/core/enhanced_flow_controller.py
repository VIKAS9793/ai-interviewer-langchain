"""
Enhanced Flow Controller with Adaptive Learning Integration
Modern AI agentic development with autonomous learning capabilities
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import json

from .adaptive_learning_system import AdaptiveLearningSystem, AdaptiveState

logger = logging.getLogger(__name__)

class EnhancedFlowController:
    """Enhanced flow controller with adaptive learning and concurrency"""
    
    def __init__(self, max_concurrent_sessions: int = 10):
        """Initialize enhanced flow controller"""
        self.adaptive_system = AdaptiveLearningSystem()
        self.max_concurrent_sessions = max_concurrent_sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_sessions)
        self.session_lock = threading.Lock()
        
        # Performance monitoring
        self.performance_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "avg_response_time": 0.0,
            "error_rate": 0.0
        }
        
        logger.info(f"Enhanced flow controller initialized with {max_concurrent_sessions} max concurrent sessions")
    
    def start_interview(self, topic: str, candidate_name: str) -> Dict[str, Any]:
        """Start interview with adaptive learning system"""
        try:
            # Check concurrency limits
            with self.session_lock:
                if len(self.active_sessions) >= self.max_concurrent_sessions:
                    return {
                        "status": "error",
                        "message": "Maximum concurrent sessions reached. Please try again later.",
                        "error_code": "CONCURRENCY_LIMIT"
                    }
            
            # Start adaptive interview
            result = self.adaptive_system.start_adaptive_interview(topic, candidate_name)
            
            if result["status"] == "started":
                # Track session
                with self.session_lock:
                    self.active_sessions[result["session_id"]] = {
                        "start_time": time.time(),
                        "topic": topic,
                        "candidate_name": candidate_name,
                        "status": "active"
                    }
                    self.performance_metrics["total_sessions"] += 1
                    self.performance_metrics["active_sessions"] = len(self.active_sessions)
                
                logger.info(f"✅ Enhanced interview started for {candidate_name} on topic: {topic}")
                
                return {
                    "session_id": result["session_id"],
                    "status": "started",
                    "first_question": result["first_question"],
                    "question_number": result["question_number"],
                    "adaptive_features": result["adaptive_features"],
                    "system_info": {
                        "concurrent_sessions": len(self.active_sessions),
                        "max_concurrent": self.max_concurrent_sessions,
                        "learning_enabled": True
                    }
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error starting enhanced interview: {e}")
            return {
                "status": "error",
                "message": f"Failed to start interview: {str(e)}",
                "error_code": "START_ERROR"
            }
    
    def process_answer(self, session: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Process answer with enhanced adaptive learning"""
        try:
            session_id = session["session_id"]
            
            # Validate session
            with self.session_lock:
                if session_id not in self.active_sessions:
                    return {
                        "status": "error",
                        "message": "Invalid session ID",
                        "error_code": "INVALID_SESSION"
                    }
                
                session_info = self.active_sessions[session_id]
                if session_info["status"] != "active":
                    return {
                        "status": "error",
                        "message": "Session is not active",
                        "error_code": "SESSION_INACTIVE"
                    }
            
            # Process with adaptive system
            start_time = time.time()
            result = self.adaptive_system.process_adaptive_answer(session, answer)
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, result["status"] == "error")
            
            if result["status"] == "continue":
                # Update session info
                with self.session_lock:
                    self.active_sessions[session_id]["last_activity"] = time.time()
                
                logger.info(f"Processed answer for session {session_id} in {processing_time:.2f}s")
                
                return {
                    "status": "continue",
                    "next_question": result["next_question"],
                    "question_number": result["question_number"],
                    "evaluation": result["evaluation"],
                    "learning_insights": result["learning_insights"],
                    "performance_metrics": {
                        "processing_time": processing_time,
                        "concurrent_sessions": len(self.active_sessions)
                    }
                }
                
            elif result["status"] == "complete":
                # Clean up completed session
                with self.session_lock:
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                        self.performance_metrics["active_sessions"] = len(self.active_sessions)
                
                logger.info(f"Completed interview for session {session_id}")
                
                return {
                    "status": "complete",
                    "final_report": result["final_report"],
                    "learning_insights": result["learning_insights"],
                    "session_data": result["session_data"],
                    "performance_metrics": {
                        "processing_time": processing_time,
                        "total_duration": time.time() - session_info["start_time"]
                    }
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error processing enhanced answer: {e}")
            return {
                "status": "error",
                "message": f"Failed to process answer: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def _update_performance_metrics(self, processing_time: float, is_error: bool):
        """Update performance metrics"""
        # Update average response time (exponential moving average)
        alpha = 0.1
        self.performance_metrics["avg_response_time"] = (
            (1 - alpha) * self.performance_metrics["avg_response_time"] + 
            alpha * processing_time
        )
        
        # Update error rate
        if is_error:
            self.performance_metrics["error_rate"] = min(1.0, self.performance_metrics["error_rate"] + 0.01)
        else:
            self.performance_metrics["error_rate"] = max(0.0, self.performance_metrics["error_rate"] - 0.001)
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced session status"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                return None
            
            session_info = self.active_sessions[session_id]
            return {
                "session_id": session_id,
                "status": session_info["status"],
                "topic": session_info["topic"],
                "candidate_name": session_info["candidate_name"],
                "start_time": session_info["start_time"],
                "last_activity": session_info.get("last_activity", session_info["start_time"]),
                "duration": time.time() - session_info["start_time"]
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        with self.session_lock:
            active_sessions = len(self.active_sessions)
        
        learning_insights = self.adaptive_system.get_learning_insights()
        
        return {
            "system_status": "operational",
            "concurrent_sessions": active_sessions,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "performance_metrics": self.performance_metrics,
            "learning_insights": learning_insights,
            "adaptive_features": {
                "learning_enabled": True,
                "adaptive_difficulty": True,
                "knowledge_tracking": True,
                "performance_analysis": True,
                "offline_optimization": True
            }
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        with self.session_lock:
            for session_id, session_info in self.active_sessions.items():
                # Session expires after 1 hour of inactivity
                if current_time - session_info.get("last_activity", session_info["start_time"]) > 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Cleaned up expired session: {session_id}")
        
        if expired_sessions:
            self.performance_metrics["active_sessions"] = len(self.active_sessions)
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get learning analytics and insights"""
        learning_insights = self.adaptive_system.get_learning_insights()
        
        return {
            "learning_metrics": learning_insights,
            "performance_trends": self.performance_metrics,
            "system_health": {
                "active_sessions": len(self.active_sessions),
                "avg_response_time": self.performance_metrics["avg_response_time"],
                "error_rate": self.performance_metrics["error_rate"],
                "learning_active": learning_insights.get("learning_active", True)
            },
            "recommendations": self._generate_system_recommendations()
        }
    
    def _generate_system_recommendations(self) -> List[str]:
        """Generate system recommendations based on performance"""
        recommendations = []
        
        # Performance-based recommendations
        if self.performance_metrics["avg_response_time"] > 5.0:
            recommendations.append("Consider optimizing question generation for faster response times")
        
        if self.performance_metrics["error_rate"] > 0.1:
            recommendations.append("High error rate detected - review system stability")
        
        if len(self.active_sessions) >= self.max_concurrent_sessions * 0.8:
            recommendations.append("High concurrent session usage - consider scaling")
        
        # Learning-based recommendations
        learning_insights = self.adaptive_system.get_learning_insights()
        if learning_insights.get("total_sessions", 0) > 100:
            recommendations.append("Sufficient data available for advanced learning optimizations")
        
        return recommendations
    
    def shutdown(self):
        """Shutdown enhanced flow controller"""
        logger.info("Shutting down enhanced flow controller...")
        
        # Shutdown adaptive system
        self.adaptive_system.shutdown()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clean up active sessions
        with self.session_lock:
            self.active_sessions.clear()
        
        logger.info("Enhanced flow controller shutdown complete")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.shutdown()
        except:
            pass  # Ignore errors during cleanup
