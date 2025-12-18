"""
Main Entry Point for ADK Interviewer.

This is the root module that ADK uses to run the agent.
Supports both `adk web` and `adk run` commands.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables (with encoding error handling)
try:
    load_dotenv(encoding='utf-8')
except Exception:
    try:
        load_dotenv(encoding='utf-16')
    except Exception:
        pass  # Will fall back to system environment variables

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Import the root agent (required by ADK)
from .agents.interviewer_agent import root_agent
from .config import validate_config

# Validate configuration on import
try:
    validate_config()
    logger.info("✅ ADK Interviewer configuration validated")
except ValueError as e:
    logger.warning(f"⚠️ Configuration issue: {e}")

# Export for ADK
__all__ = ["root_agent"]


def main():
    """
    CLI entry point for development.
    
    Usage:
        python -m adk_interviewer
    """
    print("=" * 60)
    print("🤖 AI Technical Interviewer - Google ADK Version")
    print("=" * 60)
    print()
    print("To start the web interface:")
    print("  adk web src/adk_interviewer")
    print()
    print("To run in CLI mode:")
    print("  adk run src/adk_interviewer")
    print()
    print("Environment:")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")
    print()


if __name__ == "__main__":
    main()
