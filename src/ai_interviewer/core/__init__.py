"""
AI Interviewer Core Module

Autonomous Self-Thinking AI Interview System

Research References:
    - arXiv:2509.25140 (ReasoningBank)
    - arXiv:2510.08002 (MUSE/ReflectAgent)
    - arXiv:2506.05109 (Metacognitive Learning)
    - arXiv:2512.02329 (BDIM-SE)
"""

# Autonomous AI Components
from .autonomous_reasoning_engine import (
    AutonomousReasoningEngine,
    InterviewContext,
    CandidateState,
    ThoughtChain,
    ReasoningMode
)
from .autonomous_interviewer import (
    AutonomousInterviewer,
    InterviewSession,
    InterviewPhase
)
from .autonomous_flow_controller import AutonomousFlowController

# Responsible AI Components
from .ai_guardrails import (
    ResponsibleAI,
    AIGuardrails,
    AIExplainability,
    AIAccountability,
    SafetyLevel,
    BiasCategory,
    GuardrailResult
)

# Hybrid Research-Based Components
from .reasoning_bank import (
    ReasoningBank,
    MemoryItem,
    InterviewTrajectory
)
from .reflect_agent import (
    ReflectAgent,
    ReflectionResult,
    ReflectionOutcome,
    SOP
)
from .metacognitive import (
    MetacognitiveSystem,
    BeliefSystem,
    LearningGoal,
    CapabilityLevel,
    Belief,
    Desire,
    Intention
)

# Context Engineering (CE)
from .context_engineer import (
    ContextEngineer,
    KnowledgeGrounding,
    InterviewContext as CEInterviewContext,
    ContextWindow
)

__all__ = [
    # Autonomous Core
    "AutonomousReasoningEngine",
    "AutonomousInterviewer", 
    "AutonomousFlowController",
    "InterviewContext",
    "CandidateState",
    "ThoughtChain",
    "ReasoningMode",
    "InterviewSession",
    "InterviewPhase",
    
    # Responsible AI
    "ResponsibleAI",
    "AIGuardrails",
    "AIExplainability",
    "AIAccountability",
    "SafetyLevel",
    "BiasCategory",
    "GuardrailResult",
    
    # Research-Based (Hybrid)
    "ReasoningBank",
    "MemoryItem",
    "InterviewTrajectory",
    "ReflectAgent",
    "ReflectionResult",
    "ReflectionOutcome",
    "SOP",
    "MetacognitiveSystem",
    "BeliefSystem",
    "LearningGoal",
    "CapabilityLevel",
    "Belief",
    "Desire",
    "Intention",
    
    # Context Engineering
    "ContextEngineer",
    "KnowledgeGrounding",
    "CEInterviewContext",
    "ContextWindow",
]

