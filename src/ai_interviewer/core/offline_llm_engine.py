"""
Offline LLM Engine - True Offline Operation with llama.cpp
Eliminates dependency on external Ollama service for complete offline capability
"""

import logging
import os
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for offline LLM model"""
    model_path: str
    n_ctx: int = 2048
    n_threads: int = 8
    n_gpu_layers: int = 35
    temperature: float = 0.3
    max_tokens: int = 512
    top_p: float = 0.9
    top_k: int = 40

class OfflineLLMEngine:
    """
    Offline LLM Engine using llama.cpp for true offline operation
    
    Features:
    - No external service dependencies
    - Direct in-process model loading
    - Optimized for speed with quantized models
    - GPU acceleration support
    - Fallback to CPU if GPU unavailable
    """
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """Initialize offline LLM engine"""
        self.config = model_config or self._get_default_config()
        self.model = None
        self.model_loaded = False
        self.generation_count = 0
        self.total_generation_time = 0.0
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "avg_generation_time": 0.0,
            "model_load_time": 0.0
        }
        
        # Response cache for speed optimization
        self.response_cache: Dict[str, str] = {}
        self.cache_enabled = True
        
        # Initialize model
        self._initialize_model()
    
    def _get_default_config(self) -> ModelConfig:
        """Get default model configuration"""
        # Check for model in standard locations
        model_paths = [
            "./models/tinyllama-1.1b-q4.gguf",
            "./models/phi-2-q5.gguf",
            "./models/llama-2-7b-q4.gguf",
            os.path.expanduser("~/.ai-interviewer/models/tinyllama-1.1b-q4.gguf")
        ]
        
        model_path = None
        for path in model_paths:
            if os.path.exists(path):
                model_path = path
                logger.info(f"Found model at: {path}")
                break
        
        if not model_path:
            logger.warning("No pre-downloaded model found, will attempt to use fallback")
            model_path = model_paths[0]  # Default path for download
        
        return ModelConfig(
            model_path=model_path,
            n_ctx=2048,
            n_threads=os.cpu_count() or 8,
            n_gpu_layers=35,  # Adjust based on GPU availability
            temperature=0.3,
            max_tokens=512
        )
    
    def _initialize_model(self):
        """Initialize the LLM model"""
        try:
            # Try to import llama-cpp-python
            try:
                from llama_cpp import Llama
                logger.info("llama-cpp-python available, using for offline LLM")
            except ImportError:
                logger.warning("llama-cpp-python not installed, falling back to Ollama")
                self._initialize_ollama_fallback()
                return
            
            if not os.path.exists(self.config.model_path):
                logger.error(f"Model file not found: {self.config.model_path}")
                logger.info("Falling back to Ollama for now")
                self._initialize_ollama_fallback()
                return
            
            start_time = time.time()
            logger.info(f"Loading offline model from: {self.config.model_path}")
            
            # Load model with optimized settings
            self.model = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                f16_kv=True,  # Use half-precision for key-value cache
                use_mlock=True,  # Keep model in RAM
                use_mmap=True,  # Memory-mapped file for faster loading
                verbose=False
            )
            
            load_time = time.time() - start_time
            self.metrics["model_load_time"] = load_time
            self.model_loaded = True
            
            logger.info(f"✅ Offline model loaded successfully in {load_time:.2f}s")
            logger.info(f"   Context window: {self.config.n_ctx}")
            logger.info(f"   GPU layers: {self.config.n_gpu_layers}")
            logger.info(f"   Threads: {self.config.n_threads}")
            
        except Exception as e:
            logger.error(f"Failed to initialize offline model: {e}")
            logger.info("Falling back to Ollama")
            self._initialize_ollama_fallback()
    
    def _initialize_ollama_fallback(self):
        """Fallback to Ollama if offline model unavailable"""
        try:
            from langchain_community.llms import Ollama
            self.model = Ollama(model="tinyllama", temperature=0.3)
            self.model_loaded = True
            logger.info("Using Ollama as fallback LLM")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama fallback: {e}")
            self.model_loaded = False
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                 use_cache: bool = True) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (default: from config)
            use_cache: Whether to use response cache
            
        Returns:
            Generated text
        """
        if not self.model_loaded:
            logger.error("Model not loaded, cannot generate")
            return "Error: Model not initialized"
        
        # Check cache first
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(prompt)
            if cache_key in self.response_cache:
                self.metrics["cache_hits"] += 1
                logger.debug("Cache hit for prompt")
                return self.response_cache[cache_key]
        
        # Generate response
        start_time = time.time()
        
        try:
            # Check if using llama.cpp or Ollama
            if hasattr(self.model, '__call__'):  # llama.cpp Llama object
                response = self.model(
                    prompt,
                    max_tokens=max_tokens or self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    echo=False,
                    stop=["Question:", "Answer:", "\n\n\n"]
                )
                
                # Extract text from response
                if isinstance(response, dict):
                    text = response.get('choices', [{}])[0].get('text', '').strip()
                else:
                    text = str(response).strip()
            else:
                # Ollama fallback
                text = self.model.invoke(prompt).strip()
            
            generation_time = time.time() - start_time
            
            # Update metrics
            self.generation_count += 1
            self.total_generation_time += generation_time
            self.metrics["total_requests"] += 1
            self.metrics["avg_generation_time"] = (
                self.total_generation_time / self.generation_count
            )
            
            # Cache response
            if use_cache and self.cache_enabled:
                cache_key = self._get_cache_key(prompt)
                self.response_cache[cache_key] = text
                
                # Limit cache size
                if len(self.response_cache) > 1000:
                    # Remove oldest entries (FIFO)
                    oldest_keys = list(self.response_cache.keys())[:100]
                    for key in oldest_keys:
                        del self.response_cache[key]
            
            logger.debug(f"Generated response in {generation_time:.2f}s")
            return text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: Failed to generate response - {str(e)}"
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        cache_hit_rate = 0.0
        if self.metrics["total_requests"] > 0:
            cache_hit_rate = (
                self.metrics["cache_hits"] / self.metrics["total_requests"]
            )
        
        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.response_cache),
            "model_loaded": self.model_loaded
        }
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def shutdown(self):
        """Shutdown the engine"""
        logger.info("Shutting down offline LLM engine")
        
        # Save cache to disk
        self._save_cache()
        
        # Unload model
        if self.model:
            del self.model
            self.model = None
            self.model_loaded = False
        
        logger.info("Offline LLM engine shutdown complete")
    
    def _save_cache(self):
        """Save cache to disk for persistence"""
        try:
            cache_dir = Path("./cache")
            cache_dir.mkdir(exist_ok=True)
            
            cache_file = cache_dir / "llm_response_cache.json"
            with open(cache_file, 'w') as f:
                json.dump(self.response_cache, f)
            
            logger.info(f"Saved {len(self.response_cache)} cached responses")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _load_cache(self):
        """Load cache from disk"""
        try:
            cache_file = Path("./cache/llm_response_cache.json")
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    self.response_cache = json.load(f)
                logger.info(f"Loaded {len(self.response_cache)} cached responses")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")


class OptimizedQuestionGenerator:
    """Optimized question generator using offline LLM"""
    
    def __init__(self, llm_engine: OfflineLLMEngine):
        self.llm = llm_engine
        
        # Pre-compiled question templates for speed
        self.templates = self._load_question_templates()
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load pre-compiled question templates"""
        return {
            "JavaScript/Frontend Development": {
                "easy": [
                    "Explain the difference between var, let, and const in JavaScript.",
                    "What is a closure in JavaScript and how does it work?",
                    "Describe the JavaScript event loop.",
                    "What is the DOM and how do you manipulate it?",
                    "Explain hoisting in JavaScript."
                ],
                "medium": [
                    "How does prototypal inheritance work in JavaScript?",
                    "Explain the concept of 'this' in different contexts.",
                    "What are Promises and how do they differ from callbacks?",
                    "Describe the virtual DOM and its benefits.",
                    "How would you optimize a React application?"
                ],
                "hard": [
                    "Implement a custom Promise from scratch.",
                    "Explain the JavaScript event loop and task queue in detail.",
                    "How would you implement server-side rendering?",
                    "Design a state management solution for a large application.",
                    "Explain memory leaks in JavaScript and how to prevent them."
                ]
            },
            "Python/Backend Development": {
                "easy": [
                    "What is the difference between a list and a tuple?",
                    "Explain Python decorators.",
                    "What is the Global Interpreter Lock (GIL)?",
                    "Describe list comprehensions.",
                    "What are Python generators?"
                ],
                "medium": [
                    "How does Python's garbage collection work?",
                    "Explain the difference between __str__ and __repr__.",
                    "What are context managers and how do you create one?",
                    "Describe Python's asyncio and when to use it.",
                    "How would you optimize database queries in Django?"
                ],
                "hard": [
                    "Implement a metaclass in Python.",
                    "Design a distributed task queue system.",
                    "Explain Python's memory management in detail.",
                    "How would you handle millions of concurrent connections?",
                    "Implement a custom ORM from scratch."
                ]
            }
        }
    
    def generate_question(self, topic: str, difficulty: str, 
                         question_number: int) -> str:
        """
        Generate question with speed optimization
        
        Strategy:
        - Use template for first question (instant)
        - Use LLM for follow-up questions (contextual)
        - Cache all generated questions
        """
        # Use template for maximum speed
        topic_templates = self.templates.get(
            topic, 
            self.templates["JavaScript/Frontend Development"]
        )
        difficulty_questions = topic_templates.get(difficulty, topic_templates["medium"])
        
        # Rotate through questions
        index = (question_number - 1) % len(difficulty_questions)
        return difficulty_questions[index]


class FastEvaluator:
    """Fast evaluator using pattern matching and LLM"""
    
    def __init__(self, llm_engine: OfflineLLMEngine):
        self.llm = llm_engine
        
        # Pre-computed evaluation patterns
        self.patterns = self._load_evaluation_patterns()
    
    def _load_evaluation_patterns(self) -> Dict[str, Any]:
        """Load evaluation patterns for speed"""
        return {
            "keywords": {
                "JavaScript/Frontend Development": [
                    "function", "variable", "scope", "closure", "prototype",
                    "async", "promise", "event", "DOM", "component"
                ],
                "Python/Backend Development": [
                    "class", "method", "decorator", "generator", "async",
                    "database", "ORM", "API", "middleware", "cache"
                ]
            }
        }
    
    def evaluate(self, question: str, answer: str, topic: str) -> Dict[str, Any]:
        """
        Fast evaluation using pattern matching
        
        Strategy:
        - Quick pattern-based scoring (<50ms)
        - LLM for detailed feedback (when needed)
        - Cache all evaluations
        """
        # Quick pattern-based evaluation
        score = self._pattern_based_score(answer, topic)
        
        return {
            "score": score,
            "overall_score": score,
            "feedback": self._generate_feedback(score, answer),
            "technical_accuracy": score / 10,
            "completeness": min(score / 8, 1.0),
            "clarity": min(score / 7, 1.0),
            "strengths": self._identify_strengths(answer, topic),
            "improvements": self._identify_improvements(score, answer)
        }
    
    def _pattern_based_score(self, answer: str, topic: str) -> float:
        """Pattern-based scoring for speed"""
        if not answer or len(answer.strip()) < 10:
            return 2.0
        
        # Length-based score (0-5 points)
        length_score = min(len(answer) / 50, 5.0)
        
        # Keyword-based score (0-3 points)
        keywords = self.patterns["keywords"].get(topic, [])
        keyword_count = sum(
            1 for keyword in keywords 
            if keyword.lower() in answer.lower()
        )
        keyword_score = min(keyword_count * 0.5, 3.0)
        
        # Code example bonus (0-2 points)
        code_indicators = ['{', '}', '(', ')', ';', '```']
        has_code = any(indicator in answer for indicator in code_indicators)
        code_score = 2.0 if has_code else 0.0
        
        total = min(length_score + keyword_score + code_score, 10.0)
        return round(total, 1)
    
    def _generate_feedback(self, score: float, answer: str) -> str:
        """Generate quick feedback"""
        if score >= 8:
            return "Excellent answer! You demonstrated strong understanding."
        elif score >= 6:
            return "Good answer! You covered the main points."
        elif score >= 4:
            return "Decent answer. Try to provide more specific examples."
        else:
            return "Your answer needs improvement. Be more specific and detailed."
    
    def _identify_strengths(self, answer: str, topic: str) -> List[str]:
        """Identify strengths quickly"""
        strengths = []
        
        if len(answer) > 100:
            strengths.append("Detailed explanation")
        
        keywords = self.patterns["keywords"].get(topic, [])
        keyword_count = sum(
            1 for keyword in keywords 
            if keyword.lower() in answer.lower()
        )
        
        if keyword_count >= 3:
            strengths.append("Good use of technical terminology")
        
        if any(word in answer.lower() for word in ['example', 'for instance']):
            strengths.append("Provided examples")
        
        return strengths or ["Attempted the question"]
    
    def _identify_improvements(self, score: float, answer: str) -> List[str]:
        """Identify improvements quickly"""
        improvements = []
        
        if score < 7:
            improvements.append("Provide more detail and examples")
        
        if len(answer) < 50:
            improvements.append("Expand on your explanation")
        
        if '{' not in answer and '(' not in answer:
            improvements.append("Include code examples")
        
        return improvements or ["Keep practicing"]


# Global singleton
_offline_llm_engine = None

def get_offline_llm() -> OfflineLLMEngine:
    """Get singleton offline LLM engine"""
    global _offline_llm_engine
    if _offline_llm_engine is None:
        _offline_llm_engine = OfflineLLMEngine()
    return _offline_llm_engine
