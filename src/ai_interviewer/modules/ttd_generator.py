"""
TTD Question Generator - Core Orchestrator

Implements the TTD (Test-Time Diffusion) Algorithm for question generation.
This is the Core Denoising Loop that refines questions iteratively.

Architecture (from Fareed Khan's Deep Research Agentic System):
    User Query → Research Brief → [Initial Draft Compiler] → ReAct Loop →
    Supervisor → [Core Denoising Loop] → Convergence Check → Final Output

The Core Denoising Loop:
    1. Generate initial draft (noisy)
    2. Red Team attack to find flaws
    3. Evaluate quality
    4. If quality < threshold, refine and repeat
    5. Return finalized question

Components Used:
    - QuestionEvaluator: Convergence Check (quality scoring)
    - RedTeamAgent: Noise reduction (finding flaws)
    - SemanticDeduplicator: Uniqueness validation
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TTDResult:
    """Result of TTD question generation."""
    question: str
    quality_score: float
    iterations: int
    refinements_made: List[str]
    red_team_findings: List[str]
    passed_quality: bool
    

class TTDQuestionGenerator:
    """
    TTD-based question generator with iterative refinement.
    
    Implements the Core Denoising Loop from the TTD-DR architecture:
    - Generates initial question draft
    - Uses Red Team to find flaws
    - Evaluates quality
    - Refines until convergence (quality > threshold)
    
    This approach progressively denoises the question similar to
    how diffusion models denoise images.
    """
    
    # Configuration (Optimized for Cost - Dec 17)
    MAX_ITERATIONS = 1  # Was 3. Reduced to prevent 10x call explosion.
    MIN_QUALITY_SCORE = 7.0
    CANDIDATES_COUNT = 3
    
    def __init__(self, llm=None):
        """
        Initialize TTD generator.
        
        Args:
            llm: LLM instance for question generation and refinement
        """
        self.llm = llm
        
        # Import components lazily to avoid circular imports
        from src.ai_interviewer.modules.question_evaluator import QuestionEvaluator
        from src.ai_interviewer.modules.red_team_agent import RedTeamAgent
        
        self.evaluator = QuestionEvaluator(use_llm=False)
        self.red_team = RedTeamAgent()
        
        self.generation_history: List[TTDResult] = []
        
        logger.info("🔄 TTDQuestionGenerator initialized")
    
    def generate_question(
        self,
        topic: str,
        question_number: int,
        previous_questions: Optional[List[str]] = None,
        approach: str = "balanced",
        target_difficulty: str = "medium"
    ) -> TTDResult:
        """
        Generate a high-quality question using TTD iterative refinement.
        
        This is the main entry point that orchestrates the Core Denoising Loop.
        
        Args:
            topic: Interview topic
            question_number: Which question in the interview (1-10)
            previous_questions: List of previously asked questions
            approach: Generation approach (technical, behavioral, problem-solving)
            target_difficulty: Target difficulty level (easy, medium, hard)
            
        Returns:
            TTDResult with the finalized question and metadata
        """
        previous_questions = previous_questions or []
        
        logger.info(f"🔄 TTD Generation starting for Q{question_number}: {topic}")
        
        # Step 1: Generate initial draft (noisy)
        current_question = self._generate_initial_draft(
            topic, question_number, approach, previous_questions
        )
        
        refinements = []
        red_team_findings = []
        iterations = 0
        
        # Step 2-4: Core Denoising Loop
        for iteration in range(self.MAX_ITERATIONS):
            iterations = iteration + 1
            logger.info(f"  📍 Iteration {iterations}/{self.MAX_ITERATIONS}")
            
            # Attack with Red Team
            critique = self.red_team.attack(
                current_question, 
                topic, 
                previous_questions,
                target_difficulty
            )
            
            if not critique.passed:
                red_team_findings.append(f"[Iter {iterations}] {critique.concern}")
            
            # Evaluate quality
            quality = self.evaluator.evaluate(
                current_question,
                topic,
                previous_questions,
                target_difficulty
            )
            
            # Check convergence
            if quality.passed and critique.passed:
                logger.info(f"  ✅ Converged at iteration {iterations}: {quality.overall:.1f}/10")
                break
            
            # Refinement needed
            if not critique.passed and critique.recommendation:
                logger.info(f"  🔧 Refining based on: {critique.concern}")
                refined = self._refine_question(
                    current_question, 
                    critique.recommendation,
                    topic,
                    previous_questions
                )
                if refined != current_question:
                    current_question = refined
                    refinements.append(f"Applied: {critique.recommendation[:50]}")
            elif quality.suggestions:
                logger.info(f"  🔧 Refining based on quality feedback")
                refined = self._refine_question(
                    current_question,
                    quality.suggestions[0],
                    topic,
                    previous_questions
                )
                if refined != current_question:
                    current_question = refined
                    refinements.append(f"Applied: {quality.suggestions[0][:50]}")
        
        # Final evaluation
        final_quality = self.evaluator.evaluate(
            current_question, topic, previous_questions, target_difficulty
        )
        
        result = TTDResult(
            question=current_question,
            quality_score=final_quality.overall,
            iterations=iterations,
            refinements_made=refinements,
            red_team_findings=red_team_findings,
            passed_quality=final_quality.passed
        )
        
        self.generation_history.append(result)
        
        logger.info(
            f"🔄 TTD Complete: {final_quality.overall:.1f}/10 after {iterations} iterations "
            f"({'✅ PASSED' if result.passed_quality else '⚠️ BEST EFFORT'})"
        )
        
        return result
    
    def _generate_initial_draft(
        self,
        topic: str,
        question_number: int,
        approach: str,
        previous_questions: List[str]
    ) -> str:
        """Generate initial question draft (noisy)."""
        
        if not self.llm:
            # Fallback to template-based generation
            return self._generate_fallback_question(topic, question_number, approach)
        
        history_str = "\n".join(f"- {q}" for q in previous_questions[-3:]) if previous_questions else "None"
        
        prompt = f"""[INST] Generate a unique interview question.

TOPIC: {topic}
QUESTION NUMBER: {question_number}
APPROACH: {approach}

PREVIOUSLY ASKED (DO NOT REPEAT):
{history_str}

Generate a single, clear question that:
1. Is relevant to {topic}
2. Is different from previous questions
3. Can be answered in 2-3 minutes
4. Tests technical understanding or problem-solving

Return ONLY the question text.
[/INST]"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return content.strip().replace('"', '')
        except Exception as e:
            logger.warning(f"LLM draft generation failed: {e}")
            return self._generate_fallback_question(topic, question_number, approach)
    
    def _refine_question(
        self,
        question: str,
        feedback: str,
        topic: str,
        previous_questions: List[str]
    ) -> str:
        """Refine question based on feedback."""
        
        if not self.llm:
            # Without LLM, we can't refine - just return original
            return question
        
        prompt = f"""[INST] Improve this interview question based on feedback.

ORIGINAL QUESTION: {question}
TOPIC: {topic}
FEEDBACK: {feedback}

Rewrite the question to address the feedback while keeping it:
1. Clear and specific
2. Relevant to {topic}
3. Different from questions about: {', '.join(previous_questions[-2:]) if previous_questions else 'N/A'}

Return ONLY the improved question text.
[/INST]"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            refined = content.strip().replace('"', '')
            
            # Validate it's actually a question
            if len(refined) > 10 and refined != question:
                return refined
            return question
        except Exception as e:
            logger.warning(f"Refinement failed: {e}")
            return question
    
    def _generate_fallback_question(
        self,
        topic: str,
        question_number: int,
        approach: str
    ) -> str:
        """Generate fallback question when LLM is unavailable."""
        
        fallback_templates = {
            "technical": [
                f"What are the key concepts you should know when working with {topic}?",
                f"How would you explain {topic} to a junior developer?",
                f"What common challenges have you faced when implementing {topic}?",
            ],
            "behavioral": [
                f"Describe a time when you had to learn {topic} quickly for a project.",
                f"How do you stay updated with best practices in {topic}?",
                f"Tell me about a successful {topic} project you contributed to.",
            ],
            "problem-solving": [
                f"How would you debug a complex issue involving {topic}?",
                f"What approach would you take to optimize {topic} performance?",
                f"How would you design a solution using {topic} for a scalable system?",
            ],
            "balanced": [
                f"What aspects of {topic} are you most experienced with?",
                f"How have you applied {topic} concepts in your previous work?",
                f"What would you consider best practices when working with {topic}?",
            ]
        }
        
        templates = fallback_templates.get(approach, fallback_templates["balanced"])
        idx = (question_number - 1) % len(templates)
        return templates[idx]
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics from generation history."""
        if not self.generation_history:
            return {"total": 0}
        
        avg_score = sum(r.quality_score for r in self.generation_history) / len(self.generation_history)
        avg_iterations = sum(r.iterations for r in self.generation_history) / len(self.generation_history)
        pass_rate = sum(1 for r in self.generation_history if r.passed_quality) / len(self.generation_history)
        total_refinements = sum(len(r.refinements_made) for r in self.generation_history)
        
        return {
            "total": len(self.generation_history),
            "avg_quality_score": round(avg_score, 2),
            "avg_iterations": round(avg_iterations, 2),
            "pass_rate": round(pass_rate, 2),
            "total_refinements": total_refinements
        }


# Singleton instance
_ttd_generator: Optional[TTDQuestionGenerator] = None

def get_ttd_generator(llm=None) -> TTDQuestionGenerator:
    """Get or create TTD generator instance."""
    global _ttd_generator
    if _ttd_generator is None:
        _ttd_generator = TTDQuestionGenerator(llm=llm)
    return _ttd_generator


def generate_ttd_question(
    topic: str,
    question_number: int,
    previous_questions: Optional[List[str]] = None,
    approach: str = "balanced",
    target_difficulty: str = "medium",
    llm=None
) -> str:
    """
    Convenience function to generate a single question using TTD.
    
    Returns just the question text.
    """
    generator = get_ttd_generator(llm)
    result = generator.generate_question(
        topic, question_number, previous_questions, approach, target_difficulty
    )
    return result.question
