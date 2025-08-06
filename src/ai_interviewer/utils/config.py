"""
Configuration Settings for AI Interviewer
Centralized configuration management
"""

import os
from typing import Dict, List

class Config:
    """Configuration class for AI Interviewer"""
    
    # LLM Settings
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_TEMPERATURE = 0.7
    OLLAMA_BASE_URL = "http://localhost:11434"
    
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

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    Config.LOG_LEVEL = "DEBUG"
    Config.GRADIO_SHARE = False

if os.getenv("ENVIRONMENT") == "production":
    Config.LOG_LEVEL = "WARNING"
    Config.GRADIO_SERVER_NAME = "0.0.0.0"
