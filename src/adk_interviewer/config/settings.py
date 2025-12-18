"""
Google ADK Configuration Settings.

All configuration for the pure Google-native AI Interviewer.
Uses environment variables for secure credential management.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ADKConfig:
    """Immutable configuration for ADK Interviewer."""
    
    # ============================================================
    # Google API Configuration
    # ============================================================
    
    # Gemini API Key (from Google AI Studio)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = "gemini-2.5-flash-lite"  # Free tier optimized
    MODEL_TEMPERATURE: float = 0.7
    MODEL_MAX_TOKENS: int = 2048
    
    # ============================================================
    # Interview Settings
    # ============================================================
    
    MAX_QUESTIONS: int = 5
    MIN_QUESTIONS: int = 3
    
    # Scoring thresholds
    PASSING_SCORE: float = 6.0
    EXCELLENT_SCORE: float = 8.0
    
    # Question difficulty levels
    DIFFICULTY_LEVELS: tuple = ("easy", "medium", "hard", "expert")
    
    # ============================================================
    # Safety & Guardrails
    # ============================================================
    
    ENABLE_SAFETY_FILTERS: bool = True
    ENABLE_PII_PROTECTION: bool = True
    ENABLE_BIAS_DETECTION: bool = True
    
    # Content policy
    BLOCKED_TOPICS: tuple = (
        "personal_life",
        "religion",
        "politics",
        "salary_negotiation",
        "illegal_activities"
    )
    
    # ============================================================
    # Session Management
    # ============================================================
    
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_CONCURRENT_SESSIONS: int = 10
    
    # ============================================================
    # Deployment (GCP Free Tier)
    # ============================================================
    
    GCP_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    
    # Cloud Run settings
    CLOUD_RUN_PORT: int = int(os.getenv("PORT", "8080"))
    
    # ============================================================
    # TTD (Time-Travel Diffusion) Settings
    # ============================================================
    
    TTD_MAX_ITERATIONS: int = 1  # Cost-optimized
    TTD_ENABLE_CRITIC: bool = True
    TTD_ENABLE_RESEARCH: bool = False  # Phase 2
    
    # ============================================================
    # Logging & Observability
    # ============================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_TRACING: bool = True


# Singleton instance
config = ADKConfig()


def validate_config() -> bool:
    """Validate that required configuration is present."""
    if not config.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is required. "
            "Get your key from https://aistudio.google.com/app/apikey"
        )
    return True
