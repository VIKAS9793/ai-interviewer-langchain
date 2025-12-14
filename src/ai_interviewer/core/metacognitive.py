"""
Metacognitive System: Self-Assessment and Improvement

This module implements intrinsic metacognitive learning capabilities that enable
the AI interviewer to assess its own capabilities, plan learning goals, and
continuously improve its performance.

Research Reference:
    [1] "Truly Self-Improving Agents Require Intrinsic Metacognitive Learning"
        Liu & van der Schaar
        arXiv:2506.05109 (2025)
        https://arxiv.org/abs/2506.05109
    
    [2] "Towards autonomous normative multi-agent systems"
        arXiv:2512.02329 (2025)
        BDIM-SE: Belief-Desire-Intention-Memory Architecture
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CapabilityLevel(Enum):
    """Self-assessed capability levels."""
    NOVICE = "novice"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"


@dataclass
class Belief:
    """
    Agent's belief about a state or fact.
    
    Based on BDIM-SE architecture for cognitive agents.
    Reference: arXiv:2512.02329, Section 2 "BDIM-SE"
    """
    subject: str  # What the belief is about
    predicate: str  # The belief itself
    confidence: float = 0.5  # How confident in this belief
    source: str = "observation"  # Where belief came from
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def as_tuple(self) -> tuple:
        return (self.subject, self.predicate, self.confidence)


@dataclass
class Desire:
    """
    Agent's goal or objective.
    
    Reference: arXiv:2512.02329, BDIM-SE Architecture
    """
    goal: str
    priority: int = 5  # 1-10, higher = more important
    achieved: bool = False
    deadline: Optional[str] = None


@dataclass
class Intention:
    """
    Agent's current plan or commitment.
    
    Reference: arXiv:2512.02329, BDIM-SE Architecture
    """
    action: str
    reason: str
    status: str = "pending"  # pending, active, completed, failed


@dataclass
class LearningGoal:
    """
    A specific learning improvement goal.
    
    Reference: arXiv:2506.05109, "Metacognitive Planning"
    """
    area: str  # What to improve
    target: str  # Specific improvement target
    current_level: float  # Current capability (0-1)
    target_level: float  # Target capability (0-1)
    strategy: str  # How to achieve
    progress: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BeliefSystem:
    """
    BDIM-SE inspired belief management system.
    
    Tracks agent's beliefs about:
    - Candidate state (nervous, confident, confused)
    - Interview progress
    - Topic knowledge
    - Performance trends
    
    Reference: arXiv:2512.02329, Section 2 "BDIM-SE"
    """
    
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
        self.desires: List[Desire] = []
        self.intentions: List[Intention] = []
    
    def add_belief(self, subject: str, predicate: str, 
                   confidence: float = 0.5, source: str = "observation"):
        """Add or update a belief."""
        key = f"{subject}:{predicate}"
        self.beliefs[key] = Belief(
            subject=subject,
            predicate=predicate,
            confidence=confidence,
            source=source
        )
        logger.debug(f"💭 Belief: {subject} → {predicate} ({confidence:.0%})")
    
    def get_belief(self, subject: str) -> Optional[Belief]:
        """Get beliefs about a subject."""
        for key, belief in self.beliefs.items():
            if belief.subject == subject:
                return belief
        return None
    
    def get_all_beliefs(self, subject_filter: Optional[str] = None) -> List[Belief]:
        """Get all beliefs, optionally filtered by subject."""
        beliefs = list(self.beliefs.values())
        if subject_filter:
            beliefs = [b for b in beliefs if subject_filter in b.subject]
        return beliefs
    
    def add_desire(self, goal: str, priority: int = 5):
        """Add a goal/desire."""
        self.desires.append(Desire(goal=goal, priority=priority))
    
    def add_intention(self, action: str, reason: str):
        """Add a planned action."""
        self.intentions.append(Intention(action=action, reason=reason))
        logger.debug(f"🎯 Intention: {action}")
    
    def update_candidate_state(self, state: str, confidence: float = 0.7):
        """Update belief about candidate's current state."""
        self.add_belief("candidate", f"state:{state}", confidence, "observation")
    
    def update_performance_trend(self, trend: str, confidence: float = 0.7):
        """Update belief about performance trend."""
        self.add_belief("interview", f"trend:{trend}", confidence, "analysis")


class MetacognitiveSystem:
    """
    Self-assessment and improvement system for the AI interviewer.
    
    Implements three components of metacognitive learning:
    1. Metacognitive Knowledge - Self-assessment of capabilities
    2. Metacognitive Planning - Deciding what and how to learn
    3. Metacognitive Evaluation - Reflecting on learning experiences
    
    Research Reference: arXiv:2506.05109 "Intrinsic Metacognitive Learning"
    """
    
    def __init__(self, state_path: str = "./data/memory/metacognitive_state.json"):
        """Initialize the metacognitive system."""
        self.state_path = Path(state_path)
        
        # Capability tracking by topic
        self.capabilities: Dict[str, float] = {}
        
        # Performance history
        self.performance_history: List[Dict[str, Any]] = []
        
        # Learning goals
        self.learning_goals: List[LearningGoal] = []
        
        # BDIM Belief system
        self.beliefs = BeliefSystem()
        
        # Load previous state
        self._load_state()
        
        logger.info("🧠 MetacognitiveSystem initialized")
    
    # =========================================================================
    # METACOGNITIVE KNOWLEDGE: Self-Assessment
    # =========================================================================
    
    def assess_capabilities(self) -> Dict[str, CapabilityLevel]:
        """
        Self-assess capabilities across different interview aspects.
        
        Returns capability levels for each tracked area.
        
        Reference: arXiv:2506.05109, "Metacognitive Knowledge"
        """
        assessments = {}
        
        for topic, score in self.capabilities.items():
            if score >= 0.9:
                level = CapabilityLevel.EXPERT
            elif score >= 0.75:
                level = CapabilityLevel.PROFICIENT
            elif score >= 0.6:
                level = CapabilityLevel.COMPETENT
            elif score >= 0.4:
                level = CapabilityLevel.DEVELOPING
            else:
                level = CapabilityLevel.NOVICE
            
            assessments[topic] = level
        
        logger.info(f"📊 Self-assessment completed: {len(assessments)} areas")
        return assessments
    
    def update_capability(self, topic: str, performance: float):
        """
        Update capability assessment based on performance.
        
        Uses exponential moving average to smooth updates.
        """
        alpha = 0.3  # Learning rate
        current = self.capabilities.get(topic, 0.5)
        updated = alpha * performance + (1 - alpha) * current
        
        self.capabilities[topic] = max(0.0, min(1.0, updated))
        
        logger.debug(
            f"📈 {topic} capability: {current:.2f} → {updated:.2f}"
        )
    
    def identify_weaknesses(self, threshold: float = 0.5) -> List[str]:
        """Identify areas below the competence threshold."""
        return [
            topic for topic, score in self.capabilities.items()
            if score < threshold
        ]
    
    def identify_strengths(self, threshold: float = 0.75) -> List[str]:
        """Identify areas above the proficiency threshold."""
        return [
            topic for topic, score in self.capabilities.items()
            if score >= threshold
        ]
    
    # =========================================================================
    # METACOGNITIVE PLANNING: Learning Goals
    # =========================================================================
    
    def plan_improvement(self) -> List[LearningGoal]:
        """
        Create learning goals for identified weaknesses.
        
        Reference: arXiv:2506.05109, "Metacognitive Planning"
        """
        weaknesses = self.identify_weaknesses()
        new_goals = []
        
        for topic in weaknesses:
            current = self.capabilities.get(topic, 0.3)
            
            # Skip if already has an active goal
            if any(g.area == topic and g.progress < 1.0 
                   for g in self.learning_goals):
                continue
            
            goal = LearningGoal(
                area=topic,
                target=f"Improve {topic} interview capability",
                current_level=current,
                target_level=min(0.7, current + 0.2),  # 20% improvement
                strategy=self._generate_strategy(topic, current)
            )
            
            self.learning_goals.append(goal)
            new_goals.append(goal)
        
        if new_goals:
            logger.info(f"📝 Created {len(new_goals)} learning goals")
        
        return new_goals
    
    def _generate_strategy(self, topic: str, current_level: float) -> str:
        """Generate improvement strategy based on topic and level."""
        if current_level < 0.3:
            return (
                f"Focus on fundamental {topic} concepts. "
                f"Start with basic questions and build up."
            )
        elif current_level < 0.5:
            return (
                f"Practice intermediate {topic} scenarios. "
                f"Review evaluation consistency."
            )
        else:
            return (
                f"Explore advanced {topic} topics. "
                f"Focus on nuanced evaluation criteria."
            )
    
    def update_goal_progress(self, area: str, progress_delta: float):
        """Update progress on a learning goal."""
        for goal in self.learning_goals:
            if goal.area == area:
                goal.progress = min(1.0, goal.progress + progress_delta)
                if goal.progress >= 1.0:
                    logger.info(f"🎉 Learning goal achieved: {goal.target}")
    
    # =========================================================================
    # METACOGNITIVE EVALUATION: Self-Reflection
    # =========================================================================
    
    def evaluate_performance(
        self,
        session_id: str,
        topic: str,
        scores: List[float],
        reflection_outcome: str
    ) -> Dict[str, Any]:
        """
        Evaluate own performance in an interview session.
        
        Reference: arXiv:2506.05109, "Metacognitive Evaluation"
        """
        avg_score = sum(scores) / max(1, len(scores)) if scores else 0
        
        # Normalize to 0-1 range
        performance = avg_score / 10.0
        
        # Update capability for this topic
        self.update_capability(topic, performance)
        
        # Record performance
        record = {
            "session_id": session_id,
            "topic": topic,
            "avg_score": avg_score,
            "performance": performance,
            "reflection_outcome": reflection_outcome,
            "timestamp": datetime.now().isoformat()
        }
        self.performance_history.append(record)
        
        # Update learning goals
        self.update_goal_progress(topic, 0.1 if performance > 0.6 else 0.0)
        
        # Save state
        self._save_state()
        
        # Generate self-assessment
        assessment = {
            "session_performance": performance,
            "capability_level": self.assess_capabilities().get(
                topic, CapabilityLevel.DEVELOPING
            ).value,
            "improvement_needed": performance < 0.6,
            "recommendation": self._generate_self_recommendation(
                topic, performance
            )
        }
        
        logger.info(
            f"📊 Self-evaluation: {topic} → {performance:.0%} performance"
        )
        
        return assessment
    
    def _generate_self_recommendation(
        self, 
        topic: str, 
        performance: float
    ) -> str:
        """Generate self-improvement recommendation."""
        if performance >= 0.8:
            return f"Excellent {topic} interviewing. Maintain current approach."
        elif performance >= 0.6:
            return f"Good {topic} coverage. Focus on consistency."
        elif performance >= 0.4:
            return f"Review {topic} question strategies. Improve evaluation depth."
        else:
            return f"Significant {topic} improvement needed. Study fundamentals."
    
    def get_performance_trends(
        self, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance trends over specified period."""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        recent = [
            r for r in self.performance_history
            if r.get("timestamp", "") > cutoff_str
        ]
        
        if not recent:
            return {"trend": "insufficient_data", "sessions": 0}
        
        performances = [r.get("performance", 0) for r in recent]
        avg = sum(performances) / len(performances)
        
        # Calculate trend
        if len(performances) >= 3:
            first_half = sum(performances[:len(performances)//2])
            second_half = sum(performances[len(performances)//2:])
            trend = "improving" if second_half > first_half else "declining"
        else:
            trend = "stable"
        
        # Topic breakdown
        by_topic: Dict[str, Any] = {}
        for r in recent:
            topic = r.get("topic", "unknown")
            by_topic[topic] = by_topic.get(topic, [])
            by_topic[topic].append(r.get("performance", 0))
        
        topic_avgs = {
            t: sum(scores) / len(scores) 
            for t, scores in by_topic.items()
        }
        
        return {
            "trend": trend,
            "sessions": len(recent),
            "avg_performance": avg,
            "by_topic": topic_avgs
        }
    
    # =========================================================================
    # STATE PERSISTENCE
    # =========================================================================
    
    def _save_state(self):
        """Save metacognitive state to disk."""
        state = {
            "capabilities": self.capabilities,
            "performance_history": self.performance_history[-100:],  # Keep last 100
            "learning_goals": [
                {
                    "area": g.area,
                    "target": g.target,
                    "current_level": g.current_level,
                    "target_level": g.target_level,
                    "strategy": g.strategy,
                    "progress": g.progress,
                    "created_at": g.created_at
                }
                for g in self.learning_goals
            ],
            "saved_at": datetime.now().isoformat()
        }
        
        try:
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2)
        except (IOError, OSError) as e:
            logger.warning(f"Failed to save metacognitive state: {e}")
    
    def _load_state(self):
        """Load metacognitive state from disk."""
        if not self.state_path.exists():
            return
        
        try:
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            
            self.capabilities = state.get("capabilities", {})
            self.performance_history = state.get("performance_history", [])
            
            for g_data in state.get("learning_goals", []):
                self.learning_goals.append(LearningGoal(**g_data))
            
            logger.info(
                f"📂 Loaded metacognitive state: "
                f"{len(self.capabilities)} capabilities, "
                f"{len(self.performance_history)} history records"
            )
        except Exception as e:
            logger.warning(f"Could not load metacognitive state: {e}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metacognitive summary."""
        assessments = self.assess_capabilities()
        trends = self.get_performance_trends()
        
        return {
            "capabilities": {
                k: v.value for k, v in assessments.items()
            },
            "strengths": self.identify_strengths(),
            "weaknesses": self.identify_weaknesses(),
            "active_goals": len([g for g in self.learning_goals if g.progress < 1.0]),
            "completed_goals": len([g for g in self.learning_goals if g.progress >= 1.0]),
            "performance_trend": trends.get("trend", "unknown"),
            "total_sessions": len(self.performance_history)
        }
    
    def format_for_prompt(self) -> str:
        """Format metacognitive insights for LLM prompt."""
        summary = self.get_summary()
        
        lines = ["## Self-Assessment:\n"]
        
        if summary["strengths"]:
            lines.append(f"✅ Strong in: {', '.join(summary['strengths'])}")
        
        if summary["weaknesses"]:
            lines.append(f"⚠️ Improving: {', '.join(summary['weaknesses'])}")
        
        lines.append(f"📈 Trend: {summary['performance_trend']}")
        lines.append(f"📊 Sessions analyzed: {summary['total_sessions']}")
        
        return "\n".join(lines)
