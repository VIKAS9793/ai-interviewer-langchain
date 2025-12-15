"""
Configuration Settings for AI Interviewer
Centralized configuration management
"""

import os
from typing import Dict, List, Any

class Config:
    """Configuration class for AI Interviewer"""
    
    # HuggingFace Cloud LLM Settings
    # Model Fallback Chain: Try models in order until one works
    MODEL_FALLBACK_CHAIN = [
        "google/gemma-3-4b-it",           # Primary: Newer, efficient
        "meta-llama/Meta-Llama-3-8B-Instruct",  # Fallback 1: Reliable
        "mistralai/Mistral-7B-Instruct-v0.3",   # Fallback 2: Fast
    ]
    DEFAULT_MODEL = MODEL_FALLBACK_CHAIN[0]  # Primary model
    MODEL_TEMPERATURE = 0.4
    MAX_NEW_TOKENS = 512
    MODEL_RETRY_DELAY = 2  # Seconds between model switch attempts
    
    # OpenAI Settings (Hybrid A+B: Native structured output)
    OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective with structured output support
    OPENAI_TEMPERATURE = 0.3
    
    # Google Gemini Settings (Free Tier: Gemini 2.5 Flash-Lite)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-2.5-flash-lite"  # Fastest flash model: 10 RPM, 20 RPD
    GEMINI_TEMPERATURE = 0.3
    
    # LLM Provider Priority (controls which provider to try first)
    # Options: "gemini", "openai", "huggingface", "hybrid"
    # - "gemini": Use Google Gemini (free tier, structured output)
    # - "openai": Use OpenAI (requires OPENAI_API_KEY)
    # - "huggingface": Use HuggingFace only (free, uses HF_TOKEN)
    # - "hybrid": Try Gemini -> OpenAI -> HuggingFace
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "hybrid")
    
    # Interview Settings
    MAX_QUESTIONS = 5
    DEFAULT_TOPIC = "JavaScript/Frontend Development"
    
    # Available Topics (Updated for 2024-2025 Industry)
    AVAILABLE_TOPICS = [
        "Python/Backend Development",
        "JavaScript/Frontend Development", 
        "System Design & Architecture",
        "Data Structures & Algorithms",
        "Machine Learning/AI",
        "Cloud & DevOps (AWS/GCP/Azure)",
        "Database & SQL",
        "API Design & REST"
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
    
    # Voice Mode Settings (v2.4 - Browser-Native)
    VOICE_ENABLED = True  # Feature flag
    VOICE_LANG = "en-US"  # Speech recognition/synthesis language
    VOICE_MAX_TRANSCRIPT_LENGTH = 2000  # Security: Max characters
    VOICE_RATE_LIMIT_MS = 3000  # Anti-DoS: Minimum time between recordings
    
    # Security: Input Validation Limits
    MAX_NAME_LENGTH = 100  # Maximum candidate name length
    MAX_ANSWER_LENGTH = 10000  # Maximum answer text length (allow detailed technical answers)
    MAX_JD_TEXT_LENGTH = 10000  # Maximum job description text length
    MAX_JD_URL_LENGTH = 2048  # Maximum URL length (RFC 7230)
    MAX_SCRAPED_CONTENT_LENGTH = 10000  # Maximum scraped content length
    
    # Security: Session Management
    SESSION_EXPIRATION_SECONDS = 3600  # 1 hour session expiration
    SESSION_CLEANUP_INTERVAL_SECONDS = 300  # Cleanup every 5 minutes
    
    # Security: URL Validation
    ALLOWED_URL_SCHEMES = ["http", "https"]  # Only HTTP/HTTPS allowed
    BLOCKED_HOSTNAMES = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]  # SSRF protection
    
    # Feature Flags
    LANGGRAPH_ENABLED = True  # v3.1: Use LangGraph engine
    MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "true").lower() == "true"  # Emergency: System under maintenance
    
    # Rate Limiting (Enterprise-grade API cost control)
    # Gemini 2.5 Flash-Lite Free Tier: 10 RPM, 20 RPD (Dec 2025)
    RATE_LIMIT_RPM = 10  # gemini-2.5-flash-lite actual limit
    RATE_LIMIT_RPD = 20  # gemini-2.5-flash-lite free tier
    RATE_LIMIT_MAX_CONCURRENT = 5  # Max concurrent sessions (rate limiter handles quota)
    RATE_LIMIT_TIMEOUT_SECONDS = 30  # Max wait time for rate limit
    RATE_LIMIT_MAX_RETRIES = 3  # Max retry attempts on 429 errors
    
    @classmethod
    def get_topic_mapping(cls) -> Dict[str, str]:
        """Get mapping from display names to internal names"""
        return {
            "Python/Backend Development": "python_backend",
            "JavaScript/Frontend Development": "javascript_frontend",
            "System Design & Architecture": "system_design",
            "Data Structures & Algorithms": "algorithms",
            "Machine Learning/AI": "machine_learning",
            "Cloud & DevOps (AWS/GCP/Azure)": "cloud_devops",
            "Database & SQL": "database_sql",
            "API Design & REST": "api_design"
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
        errors: List[str] = []
        warnings: List[str] = []
        is_valid = True
        
        # Validate LLM settings (HuggingFace Cloud)
        if not cls.DEFAULT_MODEL or not isinstance(cls.DEFAULT_MODEL, str):
            errors.append("DEFAULT_MODEL must be a non-empty string")
            is_valid = False
        
        if not isinstance(cls.MODEL_TEMPERATURE, (int, float)) or not (0.0 <= cls.MODEL_TEMPERATURE <= 2.0):
            errors.append("MODEL_TEMPERATURE must be a number between 0.0 and 2.0")
            is_valid = False
        
        # Validate interview settings
        if not isinstance(cls.MAX_QUESTIONS, int) or cls.MAX_QUESTIONS <= 0:
            errors.append("MAX_QUESTIONS must be a positive integer")
            is_valid = False
        
        if cls.MAX_QUESTIONS > 10:
            warnings.append("MAX_QUESTIONS is quite high, consider reducing for better user experience")
        
        # Validate topics
        if not cls.AVAILABLE_TOPICS or not isinstance(cls.AVAILABLE_TOPICS, list):
            errors.append("AVAILABLE_TOPICS must be a non-empty list")
            is_valid = False
        
        # Validate evaluation weights
        if not cls.EVALUATION_WEIGHTS or not isinstance(cls.EVALUATION_WEIGHTS, dict):
            errors.append("EVALUATION_WEIGHTS must be a dictionary")
            is_valid = False
        else:
            total_weight = sum(cls.EVALUATION_WEIGHTS.values())
            if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                warnings.append(f"EVALUATION_WEIGHTS sum to {total_weight:.3f}, should sum to 1.0")
        
        # Validate Gradio settings
        if not isinstance(cls.GRADIO_SERVER_PORT, int) or not (1024 <= cls.GRADIO_SERVER_PORT <= 65535):
            errors.append("GRADIO_SERVER_PORT must be an integer between 1024 and 65535")
            is_valid = False
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings
        }
    
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
