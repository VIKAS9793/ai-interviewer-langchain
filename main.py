"""
AI Technical Interviewer - Production-Grade Gradio UI
Clean Architecture | Responsive Design | Accessibility First
"""

import gradio as gr
import logging
import sys
import os
import socket
from pathlib import Path

# Setup project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Architecture Components
try:
    from src.ai_interviewer.controller import InterviewApplication
    from src.ui.app import create_interface
except ImportError as e:
    logger.critical(f"Failed to import core components: {e}")
    sys.exit(1)

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# ============================================================================
# UTILITIES
# ============================================================================

def is_port_available(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Application entry point"""
    print("=" * 80)
    print("AI Technical Interviewer")
    print("=" * 80)
    print(f"Python: {sys.version}")
    print(f"Gradio: {gr.__version__}")
    print(f"Project Root: {project_root}")
    print("=" * 80)
    
    try:
        # Initialize application controller
        app = InterviewApplication()
        
        # Create interface (View)
        interface = create_interface(app)
        
        # Configure for production
        interface.queue(
            default_concurrency_limit=10,
            max_size=20
        )
        
        # Find available port
        target_port = 7860
        if not is_port_available(target_port):
            logger.warning(f"Port {target_port} in use, searching for available port...")
            target_port = find_available_port(target_port)
        
        # Launch
        print(f"\n🚀 Launching application on port {target_port}...")
        interface.launch(
            server_name="0.0.0.0",
            server_port=target_port,
            share=False,
            show_error=True
        )

    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\n📋 Troubleshooting:")
        print("1. Check HF_TOKEN environment variable")
        print("2. Verify all dependencies: pip install -r requirements.txt")
        print("3. Check system resources and port availability")
        sys.exit(1)

if __name__ == "__main__":
    main()