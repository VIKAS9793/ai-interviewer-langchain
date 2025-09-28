"""
Requirements Validation Script
Quick validation of all required packages
"""

import subprocess
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def validate_requirements():
    """Validate all requirements are correctly installed"""
    print("🔍 Validating Requirements...")
    
    # Test critical imports
    imports_to_test = [
        ("langchain", "LangChain Core"),
        ("langgraph", "LangGraph State Machine"),
        ("gradio", "Gradio Web Interface"),
        ("chromadb", "ChromaDB Vector Store"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pydantic", "Pydantic Data Models"),
        ("httpx", "HTTP Client"),
        ("requests", "Requests Library")
    ]
    
    passed = 0
    failed = []
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {description} ({module})")
            passed += 1
        except ImportError:
            print(f"❌ {description} ({module}) - Run: pip install {module}")
            failed.append(module)
    
    print(f"\n📊 Results: {passed}/{len(imports_to_test)} packages validated")
    
    if failed:
        print(f"\n⚠️ Missing packages: {', '.join(failed)}")
        print(f"💡 Install missing: pip install {' '.join(failed)}")
        return False
    else:
        print("🎉 All requirements validated successfully!")
        return True

def test_core_modules():
    """Test our core application modules"""
    print("\n📦 Testing Core Application Modules...")
    
    modules_to_test = [
        ("src.ai_interviewer.agents.interviewer", "AI Interviewer Core"),
        ("src.ai_interviewer.core.flow_controller", "LangGraph Flow Controller"),
        ("src.ai_interviewer.tools.question_bank", "ChromaDB Question Bank"),
        ("src.ai_interviewer.agents.evaluator", "Answer Evaluator"),
        ("src.ai_interviewer.utils.config", "Configuration Manager")
    ]
    
    passed = 0
    
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {description} ({module}.py)")
            passed += 1
        except ImportError as e:
            print(f"❌ {description} ({module}.py) - Error: {e}")
    
    print(f"\n📊 Core Modules: {passed}/{len(modules_to_test)} modules loaded")
    return passed == len(modules_to_test)

if __name__ == "__main__":
    print("🧪 AI Interviewer - Requirements Validation")
    print("=" * 50)
    
    # Validate requirements
    req_valid = validate_requirements()
    
    # Test core modules
    modules_valid = test_core_modules()
    
    print("\n" + "=" * 50)
    if req_valid and modules_valid:
        print("🎉 All validations passed! Ready to run AI Interviewer!")
        print("\n🚀 Next steps:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull model: ollama pull llama3.2:3b")
        print("3. Run: python main.py")
        sys.exit(0)
    else:
        print("❌ Some validations failed. Fix issues above.")
        sys.exit(1)
