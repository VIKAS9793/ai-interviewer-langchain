"""
Configuration Settings for AI Interviewer
Centralized configuration management
"""

import os
from typing import Dict, List, Any

class Config:
    """Configuration class for AI Interviewer"""
    
    # HuggingFace Cloud LLM Settings
    DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
    MODEL_TEMPERATURE = 0.4
    MAX_NEW_TOKENS = 512
    
    # Interview Settings
    MAX_QUESTIONS = 5
    DEFAULT_TOPIC = "JavaScript/Frontend Development"
    
    # Available Topics
    AVAILABLE_TOPICS = [
        "JavaScript/Frontend Development",
        "Python/Backend Development", 
        "Machine Learning/AI",
        "System Design",
        "Data Structures & Algorithms"
    ]
    
    # Gradio Settings
    GRADIO_SERVER_NAME = "127.0.0.1"
    GRADIO_SERVER_PORT = 7860
    GRADIO_SHARE = False
    
    # ChromaDB Settings
    CHROMADB_PERSIST_DIRECTORY = "./chroma_db"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Evaluation Weights
    EVALUATION_WEIGHTS = {
        "technical_accuracy": 0.25,
        "conceptual_understanding": 0.25,
        "practical_application": 0.20,
        "communication_clarity": 0.15,
        "depth_of_knowledge": 0.10,
        "problem_solving_approach": 0.05
    }
    
    # Logging Settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Evaluation Model Settings (Unified Architecture)
    EVALUATION_MODEL = DEFAULT_MODEL  # Use primary model for evaluation (Stability)
    EVALUATION_TEMPERATURE = 0.1  # Low temp for consistent scoring
    EVALUATION_SCALE = 5  # 1-5 scale (more reliable than 1-10)
    
    @classmethod
    def get_topic_mapping(cls) -> Dict[str, str]:
        """Get mapping from display names to internal names"""
        return {
            "JavaScript/Frontend Development": "javascript_frontend",
            "Python/Backend Development": "python_backend",
            "Machine Learning/AI": "machine_learning",
            "System Design": "system_design",
            "Data Structures & Algorithms": "algorithms"
        }
    
    @classmethod
    def validate_topic(cls, topic: str) -> bool:
        """Validate if topic is supported"""
        return topic in cls.AVAILABLE_TOPICS
    
    @classmethod
    def get_difficulty_levels(cls) -> List[str]:
        """Get available difficulty levels"""
        return ["easy", "medium", "hard"]
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate all configuration settings"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate LLM settings (HuggingFace Cloud)
        if not cls.DEFAULT_MODEL or not isinstance(cls.DEFAULT_MODEL, str):
            validation_results["errors"].append("DEFAULT_MODEL must be a non-empty string")
            validation_results["valid"] = False
        
        if not isinstance(cls.MODEL_TEMPERATURE, (int, float)) or not (0.0 <= cls.MODEL_TEMPERATURE <= 2.0):
            validation_results["errors"].append("MODEL_TEMPERATURE must be a number between 0.0 and 2.0")
            validation_results["valid"] = False
        
        # Validate interview settings
        if not isinstance(cls.MAX_QUESTIONS, int) or cls.MAX_QUESTIONS <= 0:
            validation_results["errors"].append("MAX_QUESTIONS must be a positive integer")
            validation_results["valid"] = False
        
        if cls.MAX_QUESTIONS > 10:
            validation_results["warnings"].append("MAX_QUESTIONS is quite high, consider reducing for better user experience")
        
        # Validate topics
        if not cls.AVAILABLE_TOPICS or not isinstance(cls.AVAILABLE_TOPICS, list):
            validation_results["errors"].append("AVAILABLE_TOPICS must be a non-empty list")
            validation_results["valid"] = False
        
        # Validate evaluation weights
        if not cls.EVALUATION_WEIGHTS or not isinstance(cls.EVALUATION_WEIGHTS, dict):
            validation_results["errors"].append("EVALUATION_WEIGHTS must be a dictionary")
            validation_results["valid"] = False
        else:
            total_weight = sum(cls.EVALUATION_WEIGHTS.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                validation_results["warnings"].append(f"EVALUATION_WEIGHTS sum to {total_weight:.3f}, should sum to 1.0")
        
        # Validate Gradio settings
        if not isinstance(cls.GRADIO_SERVER_PORT, int) or not (1024 <= cls.GRADIO_SERVER_PORT <= 65535):
            validation_results["errors"].append("GRADIO_SERVER_PORT must be an integer between 1024 and 65535")
            validation_results["valid"] = False
        
        return validation_results
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "llm_model": cls.DEFAULT_MODEL,
            "llm_temperature": cls.MODEL_TEMPERATURE,
            "evaluation_model": cls.EVALUATION_MODEL,
            "max_questions": cls.MAX_QUESTIONS,
            "available_topics": len(cls.AVAILABLE_TOPICS),
            "evaluation_dimensions": len(cls.EVALUATION_WEIGHTS)
        }

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    Config.LOG_LEVEL = "DEBUG"
    Config.GRADIO_SHARE = False

if os.getenv("ENVIRONMENT") == "production":
    Config.LOG_LEVEL = "WARNING"
    Config.GRADIO_SERVER_NAME = "0.0.0.0"
