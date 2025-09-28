"""
Test Setup Script - Verify AI Interviewer Components
Quick validation of core dependencies and functionality
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing Core Imports...")
    
    try:
        # Core Python
        import json
        import time
        from typing import Dict, List, Any
        print("✅ Core Python modules")
        
        # Pydantic
        from pydantic import BaseModel, Field
        print("✅ Pydantic")
        
        # LangChain Core
        from langchain.prompts import PromptTemplate
        print("✅ LangChain Core")
        
        # LangGraph
        from langgraph.graph import StateGraph, END
        print("✅ LangGraph")
        
        # Gradio
        import gradio as gr
        print("✅ Gradio")
        
        # ChromaDB
        import chromadb
        print("✅ ChromaDB")
        
        # Sentence Transformers
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False

def test_ollama_connection():
    """Test Ollama LLM connection"""
    print("\n🤖 Testing Ollama Connection...")
    
    try:
        from langchain_community.llms import Ollama
        
        # Try to initialize Ollama
        llm = Ollama(model="llama3.2:3b", temperature=0.1)
        
        # Simple test
        response = llm.invoke("Hello")
        print(f"✅ Ollama Response: {response[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 And model is pulled: ollama pull llama3.2:3b")
        return False

def test_chromadb():
    """Test ChromaDB initialization"""
    print("\n🗄️ Testing ChromaDB...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize client
        client = chromadb.Client(Settings(anonymized_telemetry=False))
        
        # Create test collection
        collection = client.create_collection(name="test_collection")
        
        # Add test document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"type": "test"}],
            ids=["test_1"]
        )
        
        # Query test
        results = collection.query(query_texts=["test"], n_results=1)
        
        # Cleanup
        client.delete_collection(name="test_collection")
        
        print("✅ ChromaDB working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
        return False

def test_gradio():
    """Test Gradio interface creation"""
    print("\n🌐 Testing Gradio...")
    
    try:
        import gradio as gr
        
        # Create simple interface
        def test_function(text):
            return f"Echo: {text}"
        
        interface = gr.Interface(
            fn=test_function,
            inputs="text",
            outputs="text",
            title="Test Interface"
        )
        
        print("✅ Gradio interface created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Gradio Error: {e}")
        return False

def test_core_modules():
    """Test our core modules can be imported"""
    print("\n📦 Testing Core Modules...")
    
    try:
        # Test interviewer module
        from interviewer import AIInterviewer, QuestionResponse, AnswerEvaluation
        print("✅ Interviewer module")
        
        # Test flow controller
        from flow_controller import InterviewFlowController, InterviewState
        print("✅ Flow Controller module")
        
        # Test question bank
        from question_bank import QuestionBank
        print("✅ Question Bank module")
        
        # Test evaluator
        from evaluator import AdvancedEvaluator
        print("✅ Evaluator module")
        
        return True
        
    except Exception as e:
        print(f"❌ Core Module Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Interviewer Setup Test")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_imports),
        ("Core Modules", test_core_modules),
        ("ChromaDB", test_chromadb),
        ("Gradio", test_gradio),
        ("Ollama Connection", test_ollama_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready to run the AI Interviewer!")
        print("\n🚀 Next steps:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull llama3.2:3b")
        print("3. Run the app: python main.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
