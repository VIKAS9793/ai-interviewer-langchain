"""
AI Interviewer Launcher Script
Handles environment setup and graceful startup
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_ollama():
    """Check if Ollama is available"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            if "llama3.1:8b" in result.stdout:
                print("✅ Ollama and llama3.1:8b model available")
                return True
            else:
                print("⚠️ Ollama available but llama3.1:8b model not found")
                print("💡 Run: ollama pull llama3.1:8b")
                return False
        else:
            print("❌ Ollama not responding")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not found or not running")
        print("💡 Install Ollama: https://ollama.ai/")
        print("💡 Start Ollama: ollama serve")
        return False

def check_virtual_env():
    """Check if we're in a virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
        return True
    else:
        print("⚠️ No virtual environment detected")
        print("💡 Recommended: python -m venv venv && venv\\Scripts\\activate")
        return False

def check_dependencies():
    """Check if key dependencies are installed"""
    required_packages = [
        "langchain",
        "langgraph", 
        "gradio",
        "chromadb",
        "sentence_transformers"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"💡 Install missing packages: pip install {' '.join(missing)}")
        return False
    
    return True

def run_tests():
    """Run basic setup tests"""
    try:
        print("\n🧪 Running setup tests...")
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def launch_app():
    """Launch the main application"""
    try:
        print("\n🚀 Launching AI Interviewer...")
        print("🌐 Opening browser at: http://localhost:7860")
        print("⏹️ Press Ctrl+C to stop")
        
        # Run the main app
        subprocess.run([sys.executable, "main.py"])
        
    except KeyboardInterrupt:
        print("\n👋 AI Interviewer stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")

def main():
    """Main launcher function"""
    logger = setup_logging()
    
    print("🤖 AI Technical Interviewer - Launcher")
    print("=" * 50)
    
    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Dependencies", check_dependencies),
        ("Ollama Setup", check_ollama),
    ]
    
    passed = 0
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        if check_func():
            passed += 1
        else:
            print(f"⚠️ {check_name} check failed")
    
    print(f"\n📊 Pre-flight: {passed}/{len(checks)} checks passed")
    
    if passed < len(checks):
        print("\n⚠️ Some checks failed. Fix the issues above before continuing.")
        
        # Ask user if they want to continue anyway
        try:
            response = input("\nContinue anyway? (y/N): ").lower()
            if response != 'y':
                print("👋 Exiting...")
                return False
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return False
    
    # Run tests if test_setup.py exists
    if Path("test_setup.py").exists():
        if not run_tests():
            print("⚠️ Tests failed but continuing...")
    
    # Launch the application
    launch_app()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted by user")
        sys.exit(0)
