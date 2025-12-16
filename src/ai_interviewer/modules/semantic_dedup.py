"""
Semantic Question Deduplicator Module

This module provides embedding-based semantic similarity detection
to prevent duplicate questions in AI interviews.

The problem: Previous implementation used substring matching which
missed semantic duplicates like:
  - "Tell me about a challenge" vs "Describe a difficult situation"

The solution: Use sentence embeddings to detect semantic similarity.
If cosine similarity > threshold (0.75), the question is considered
a duplicate and should be blocked/regenerated.

References:
  - sentence-transformers: https://www.sbert.net/
  - Model: all-MiniLM-L6-v2 (fast, 22MB, good quality)
"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, fallback to basic matching if unavailable
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Using fallback string matching.")


class SemanticDeduplicator:
    """
    Detects semantically similar questions using embeddings.
    
    Usage:
        dedup = SemanticDeduplicator()
        if dedup.is_duplicate("new question", ["prev q1", "prev q2"]):
            # regenerate question
    """
    
    # Singleton model to avoid reloading
    _model = None
    _model_name = "all-MiniLM-L6-v2"
    
    def __init__(self, similarity_threshold: float = 0.70):
        """
        Initialize the deduplicator.
        
        Args:
            similarity_threshold: Cosine similarity above this = duplicate (0.0-1.0)
                                  Default 0.75 is balanced for interview questions.
        """
        self.threshold = similarity_threshold
        self._ensure_model_loaded()
    
    @classmethod
    def _ensure_model_loaded(cls):
        """Load embedding model once (singleton pattern)."""
        if EMBEDDINGS_AVAILABLE and cls._model is None:
            try:
                logger.info(f"Loading embedding model: {cls._model_name}")
                cls._model = SentenceTransformer(cls._model_name)
                logger.info("✅ Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                cls._model = None
    
    def is_duplicate(
        self, 
        new_question: str, 
        previous_questions: List[str],
        return_score: bool = False
    ) -> bool:
        """
        Check if new_question is semantically similar to any previous question.
        
        Args:
            new_question: The candidate question to check
            previous_questions: List of previously asked questions
            return_score: If True, return (is_duplicate, max_similarity) tuple
        
        Returns:
            True if duplicate detected, False otherwise
            If return_score=True, returns (bool, float)
        """
        if not previous_questions:
            return (False, 0.0) if return_score else False
        
        # Use embeddings if available
        if EMBEDDINGS_AVAILABLE and self._model is not None:
            return self._check_with_embeddings(new_question, previous_questions, return_score)
        else:
            return self._check_with_fallback(new_question, previous_questions, return_score)
    
    def _check_with_embeddings(
        self, 
        new_question: str, 
        previous_questions: List[str],
        return_score: bool
    ) -> bool:
        """Embedding-based semantic similarity check."""
        try:
            # Encode all questions
            new_embedding = self._model.encode(new_question, convert_to_numpy=True)
            prev_embeddings = self._model.encode(previous_questions, convert_to_numpy=True)
            
            # Calculate cosine similarities
            max_similarity = 0.0
            for prev_emb in prev_embeddings:
                similarity = self._cosine_similarity(new_embedding, prev_emb)
                max_similarity = max(max_similarity, similarity)
                
                if similarity > self.threshold:
                    logger.warning(
                        f"⚠️ Semantic duplicate detected (similarity: {similarity:.2f}): "
                        f"'{new_question[:50]}...'"
                    )
                    return (True, similarity) if return_score else True
            
            logger.debug(f"✅ Question unique (max similarity: {max_similarity:.2f})")
            return (False, max_similarity) if return_score else False
            
        except Exception as e:
            logger.error(f"Embedding check failed: {e}, using fallback")
            return self._check_with_fallback(new_question, previous_questions, return_score)
    
    def _check_with_fallback(
        self, 
        new_question: str, 
        previous_questions: List[str],
        return_score: bool
    ) -> bool:
        """
        Fallback: Basic string matching when embeddings unavailable.
        Uses normalized Levenshtein-like comparison.
        """
        new_lower = new_question.lower().strip()
        new_words = set(new_lower.split())
        
        max_similarity = 0.0
        for prev_q in previous_questions:
            prev_lower = prev_q.lower().strip()
            prev_words = set(prev_lower.split())
            
            # Jaccard similarity
            if new_words or prev_words:
                intersection = len(new_words & prev_words)
                union = len(new_words | prev_words)
                similarity = intersection / union if union > 0 else 0
                max_similarity = max(max_similarity, similarity)
                
                if similarity > self.threshold:
                    logger.warning(f"⚠️ Fallback duplicate detected (Jaccard: {similarity:.2f})")
                    return (True, similarity) if return_score else True
            
            # Also check substring (original logic)
            if prev_lower in new_lower or new_lower in prev_lower:
                logger.warning("⚠️ Substring duplicate detected")
                return (True, 1.0) if return_score else True
        
        return (False, max_similarity) if return_score else False
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))


# Singleton instance for easy access
_deduplicator_instance: Optional[SemanticDeduplicator] = None

def get_deduplicator(threshold: float = 0.75) -> SemanticDeduplicator:
    """Get or create singleton deduplicator instance."""
    global _deduplicator_instance
    if _deduplicator_instance is None:
        _deduplicator_instance = SemanticDeduplicator(threshold)
    return _deduplicator_instance


def is_semantic_duplicate(new_question: str, previous_questions: List[str]) -> bool:
    """
    Convenience function to check for semantic duplicates.
    
    Usage:
        from src.ai_interviewer.modules.semantic_dedup import is_semantic_duplicate
        
        if is_semantic_duplicate(new_q, prev_questions):
            # regenerate
    """
    return get_deduplicator().is_duplicate(new_question, previous_questions)
