"""
Type definitions for AI Interviewer.

This module provides TypedDict models and type aliases for better type safety
and IDE support throughout the codebase.
"""

from typing import TypedDict, List, Optional, Dict, Any, Union
from datetime import datetime


class InterviewResponse(TypedDict, total=False):
    """Standard interview response format"""
    success: bool
    status: str  # "started" | "continue" | "completed" | "error"
    session_id: str
    greeting: Optional[str]
    first_question: Optional[str]
    next_question: Optional[str]
    question: Optional[str]
    question_number: int
    total_questions: int
    topic: str
    evaluation: Optional[Dict[str, Any]]
    feedback: Optional[str]
    reasoning: Optional[Dict[str, Any]]
    summary: Optional[Dict[str, Any]]
    elapsed: Optional[int]
    message: Optional[str]
    current_data: Optional[Dict[str, Any]]
    # Error response fields (when success=False)
    error_code: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: Optional[str]


class ErrorResponse(TypedDict):
    """Standard error response format"""
    success: bool
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
    timestamp: str


class PracticeModeResponse(TypedDict, total=False):
    """Response format for practice mode interview"""
    success: bool
    session_id: str
    greeting: str
    first_question: str
    question_number: int
    total_questions: int
    topic: str
    experience_level: str
    detected_skills: List[str]
    job_title: Optional[str]
    company_name: Optional[str]
    message: Optional[str]
    # Error response fields (when success=False)
    error_code: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: Optional[str]


class EvaluationResult(TypedDict, total=False):
    """Evaluation result structure"""
    score: float
    max_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    confidence: float


class SessionData(TypedDict, total=False):
    """Session data structure"""
    session_id: str
    topic: str
    candidate_name: str
    question_count: int
    start_time: float
    mode: Optional[str]  # "topic" | "practice"


class ResumeAnalysisResult(TypedDict, total=False):
    """Resume analysis result structure"""
    skills: List[str]
    experience_level: str
    detected_role: Optional[str]
    suggested_topics: List[str]
    key_qualifications: List[str]
    summary: str
    experience_years: int


class JDParseResult(TypedDict, total=False):
    """Job description parsing result"""
    role_title: Optional[str]
    company_name: Optional[str]
    requirements: List[str]
    location: Optional[str]
    salary: Optional[str]


class InterviewStartResponse(TypedDict, total=False):
    """Response from start_interview"""
    status: str  # "started" | "error"
    session_id: str
    greeting: str
    first_question: str
    message: Optional[str]
    error_code: Optional[str]
    # Error response fields (when status="error")
    success: Optional[bool]
    details: Optional[Dict[str, Any]]
    timestamp: Optional[str]


class AnswerProcessResponse(TypedDict, total=False):
    """Response from process_answer"""
    status: str  # "continue" | "completed" | "error"
    next_question: Optional[str]
    question_number: int
    evaluation: Optional[EvaluationResult]
    feedback: Optional[str]
    reasoning: Optional[Dict[str, Any]]
    final_report: Optional[str]
    summary: Optional[Dict[str, Any]]
    message: Optional[str]
    error_code: Optional[str]
    # Error response fields (when status="error")
    success: Optional[bool]
    details: Optional[Dict[str, Any]]
    timestamp: Optional[str]


class SessionStatusResponse(TypedDict, total=False):
    """Session status response"""
    session_id: str
    status: str
    question_number: int
    total_questions: int
    candidate_name: str
    topic: str
    phase: str
    elapsed_time: float


class SystemStatusResponse(TypedDict, total=False):
    """System status response"""
    active_sessions: int
    total_sessions: int
    avg_response_time: float
    autonomous_decisions: int
    self_recoveries: int
    # Additional fields that may be included
    status: Optional[str]
    autonomous_features: Optional[Dict[str, Any]]
    performance: Optional[Dict[str, Any]]
    interviewer_stats: Optional[Dict[str, Any]]
    capacity: Optional[int]


class ResumeAnalysisResponse(TypedDict, total=False):
    """Resume analysis response (extends ResumeAnalysisResult)"""
    skills: List[str]
    experience_level: str
    detected_role: Optional[str]
    suggested_topics: List[str]
    key_qualifications: List[str]
    summary: str
    experience_years: int


class InterviewSummaryResponse(TypedDict, total=False):
    """Interview summary response"""
    session_id: str
    candidate_name: str
    topic: str
    total_questions: int
    avg_score: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    overall_assessment: str


# Type aliases for common patterns
GradioFile = Union[str, Any]  # Gradio file object type (varies by version)
AudioData = tuple  # (sample_rate, audio_array)

