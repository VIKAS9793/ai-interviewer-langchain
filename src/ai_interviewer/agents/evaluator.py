"""
Answer Evaluator - Advanced Scoring and Feedback System
Multi-dimensional evaluation with professional feedback
"""

import logging
from typing import Dict, List, Any, Optional
import re
import json
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class AdvancedEvaluator:
    """Advanced answer evaluation with multiple scoring dimensions"""
    
    def __init__(self):
        """Initialize the evaluator with LLM and scoring criteria"""
        try:
            from ..utils.config import Config
            self.llm = Ollama(
                model=Config.OLLAMA_MODEL,
                temperature=0.3  # Lower temperature for more consistent evaluation
            )
            
            # Test LLM connection
            test_response = self.llm.invoke("Test")
            logger.info("✅ Evaluator LLM connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize evaluator LLM: {e}")
            raise
    
    def evaluate_comprehensive(self, question: str, answer: str, topic: str, 
                             expected_concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive multi-dimensional answer evaluation"""
        
        evaluation_prompt = PromptTemplate(
            input_variables=["question", "answer", "topic", "expected_concepts"],
            template="""You are a senior technical interviewer evaluating a candidate's answer.

QUESTION: {question}
TOPIC: {topic}
CANDIDATE'S ANSWER: {answer}
EXPECTED CONCEPTS: {expected_concepts}

Evaluate this answer across multiple dimensions on a scale of 1-10:

1. TECHNICAL ACCURACY (1-10): How technically correct and accurate is the answer?
2. CONCEPTUAL UNDERSTANDING (1-10): How well does the candidate understand the underlying concepts?
3. PRACTICAL APPLICATION (1-10): How well can the candidate apply this knowledge practically?
4. COMMUNICATION CLARITY (1-10): How clearly and effectively is the answer communicated?
5. DEPTH OF KNOWLEDGE (1-10): How deep is the candidate's understanding of the topic?
6. PROBLEM-SOLVING APPROACH (1-10): How well does the answer demonstrate problem-solving skills?

Also provide:
- Overall score (1-10) - weighted average
- Key strengths (2-3 points)
- Areas for improvement (2-3 points)
- Missing concepts (if any)
- Recommended next difficulty level (easy/medium/hard)
- Confidence level in evaluation (0.0-1.0)

Respond in JSON format:
{{
    "technical_accuracy": <score>,
    "conceptual_understanding": <score>,
    "practical_application": <score>,
    "communication_clarity": <score>,
    "depth_of_knowledge": <score>,
    "problem_solving_approach": <score>,
    "overall_score": <weighted_average>,
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"],
    "missing_concepts": ["concept1", "concept2"],
    "next_difficulty": "medium",
    "confidence": 0.85,
    "detailed_feedback": "Comprehensive feedback paragraph"
}}"""
        )
        
        try:
            # Prepare expected concepts
            concepts_str = ", ".join(expected_concepts) if expected_concepts else "Not specified"
            
            # Generate evaluation
            chain = evaluation_prompt | self.llm
            response = chain.invoke({
                "question": question,
                "answer": answer,
                "topic": topic,
                "expected_concepts": concepts_str
            })
            
            # Parse JSON response
            evaluation = json.loads(response.strip())
            
            # Add additional metrics
            evaluation.update(self._calculate_additional_metrics(answer, expected_concepts))
            
            logger.info(f"Comprehensive evaluation completed - Overall score: {evaluation.get('overall_score', 0)}/10")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in comprehensive evaluation: {e}")
            return self._fallback_evaluation(question, answer, topic, expected_concepts)
    
    def evaluate_quick(self, question: str, answer: str, topic: str) -> Dict[str, Any]:
        """Quick evaluation for faster processing"""
        
        quick_prompt = PromptTemplate(
            input_variables=["question", "answer", "topic"],
            template="""Quickly evaluate this technical interview answer on a scale of 1-10:

QUESTION: {question}
ANSWER: {answer}
TOPIC: {topic}

Provide scores for:
- Technical accuracy (1-10)
- Communication clarity (1-10)
- Overall score (1-10)
- One key strength
- One improvement area
- Next difficulty (easy/medium/hard)

JSON format:
{{
    "technical_accuracy": <score>,
    "communication_clarity": <score>,
    "overall_score": <score>,
    "strengths": ["<strength>"],
    "improvements": ["<improvement>"],
    "next_difficulty": "<difficulty>"
}}"""
        )
        
        try:
            chain = quick_prompt | self.llm
            response = chain.invoke({
                "question": question,
                "answer": answer,
                "topic": topic
            })
            
            evaluation = json.loads(response.strip())
            
            # Add basic metrics
            evaluation.update({
                "evaluation_type": "quick",
                "confidence": 0.7,
                "word_count": len(answer.split()),
                "answer_length": len(answer)
            })
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in quick evaluation: {e}")
            return self._fallback_evaluation(question, answer, topic)
    
    def _calculate_additional_metrics(self, answer: str, expected_concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate additional metrics for the answer"""
        metrics = {}
        
        # Basic text metrics
        words = answer.split()
        metrics["word_count"] = len(words)
        metrics["character_count"] = len(answer)
        metrics["sentence_count"] = len(re.split(r'[.!?]+', answer))
        
        # Complexity indicators
        metrics["avg_word_length"] = sum(len(word) for word in words) / len(words) if words else 0
        metrics["technical_terms"] = self._count_technical_terms(answer)
        
        # Concept coverage
        if expected_concepts:
            covered_concepts = self._check_concept_coverage(answer, expected_concepts)
            metrics["concept_coverage"] = len(covered_concepts) / len(expected_concepts)
            metrics["covered_concepts"] = covered_concepts
        else:
            metrics["concept_coverage"] = 0.0
            metrics["covered_concepts"] = []
        
        # Answer quality indicators
        metrics["has_examples"] = bool(re.search(r'\b(example|for instance|such as|like)\b', answer.lower()))
        metrics["has_code"] = bool(re.search(r'[{}();]', answer))
        metrics["question_marks"] = answer.count('?')
        
        return metrics
    
    def _count_technical_terms(self, answer: str) -> int:
        """Count technical terms in the answer"""
        technical_terms = [
            'algorithm', 'function', 'variable', 'class', 'object', 'method',
            'array', 'string', 'integer', 'boolean', 'loop', 'condition',
            'database', 'query', 'index', 'optimization', 'performance',
            'scalability', 'architecture', 'framework', 'library', 'api',
            'async', 'sync', 'callback', 'promise', 'thread', 'process'
        ]
        
        answer_lower = answer.lower()
        count = sum(1 for term in technical_terms if term in answer_lower)
        return count
    
    def _check_concept_coverage(self, answer: str, expected_concepts: List[str]) -> List[str]:
        """Check which expected concepts are covered in the answer"""
        answer_lower = answer.lower()
        covered = []
        
        for concept in expected_concepts:
            # Simple keyword matching - could be improved with NLP
            if concept.lower() in answer_lower:
                covered.append(concept)
        
        return covered
    
    def _fallback_evaluation(self, question: str, answer: str, topic: str, 
                           expected_concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fallback evaluation when LLM fails"""
        
        # Heuristic scoring based on answer characteristics
        word_count = len(answer.split())
        
        # Base score from answer length
        if word_count > 100:
            base_score = 8
        elif word_count > 50:
            base_score = 7
        elif word_count > 20:
            base_score = 6
        elif word_count > 10:
            base_score = 5
        else:
            base_score = 3
        
        # Adjust for technical content
        technical_score = min(10, base_score + self._count_technical_terms(answer))
        
        # Concept coverage bonus
        concept_bonus = 0
        if expected_concepts:
            covered = self._check_concept_coverage(answer, expected_concepts)
            concept_bonus = len(covered)
        
        final_score = min(10, (technical_score + concept_bonus) // 2)
        
        return {
            "technical_accuracy": final_score,
            "conceptual_understanding": final_score,
            "practical_application": max(1, final_score - 1),
            "communication_clarity": min(10, final_score + 1),
            "depth_of_knowledge": final_score,
            "problem_solving_approach": final_score,
            "overall_score": final_score,
            "strengths": ["Provided a response", "Attempted to answer the question"],
            "improvements": ["Could provide more technical detail", "Consider adding examples"],
            "missing_concepts": expected_concepts[:2] if expected_concepts else [],
            "next_difficulty": "medium" if final_score >= 6 else "easy",
            "confidence": 0.5,
            "detailed_feedback": f"Answer demonstrates basic understanding. Score based on length ({word_count} words) and technical content.",
            "evaluation_type": "fallback",
            "word_count": word_count,
            "technical_terms": self._count_technical_terms(answer)
        }
    
    def generate_improvement_suggestions(self, evaluation: Dict[str, Any], topic: str) -> List[str]:
        """Generate specific improvement suggestions based on evaluation"""
        
        suggestions = []
        overall_score = evaluation.get("overall_score", 5)
        
        # Score-based suggestions
        if overall_score < 4:
            suggestions.extend([
                f"Review fundamental {topic} concepts",
                "Practice explaining technical concepts clearly",
                "Study basic terminology and definitions"
            ])
        elif overall_score < 7:
            suggestions.extend([
                f"Deepen your understanding of {topic}",
                "Practice with more complex examples",
                "Work on connecting concepts together"
            ])
        else:
            suggestions.extend([
                f"Explore advanced {topic} topics",
                "Practice system design and architecture",
                "Focus on real-world applications"
            ])
        
        # Dimension-specific suggestions
        if evaluation.get("technical_accuracy", 5) < 6:
            suggestions.append("Focus on technical accuracy and correctness")
        
        if evaluation.get("communication_clarity", 5) < 6:
            suggestions.append("Practice explaining concepts more clearly")
        
        if evaluation.get("practical_application", 5) < 6:
            suggestions.append("Study real-world applications and use cases")
        
        # Remove duplicates and limit to top 5
        suggestions = list(dict.fromkeys(suggestions))[:5]
        
        return suggestions
    
    def compare_evaluations(self, eval1: Dict[str, Any], eval2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two evaluations to show improvement/decline"""
        
        comparison = {
            "overall_change": eval2.get("overall_score", 0) - eval1.get("overall_score", 0),
            "technical_change": eval2.get("technical_accuracy", 0) - eval1.get("technical_accuracy", 0),
            "communication_change": eval2.get("communication_clarity", 0) - eval1.get("communication_clarity", 0),
            "trend": "improving" if eval2.get("overall_score", 0) > eval1.get("overall_score", 0) else "declining" if eval2.get("overall_score", 0) < eval1.get("overall_score", 0) else "stable"
        }
        
        return comparison
