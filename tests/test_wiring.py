
import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WiringTest")

def test_wiring():
    """Verify InterviewApplication initializes InterviewGraph correctly"""
    logger.info("🧪 Testing Application Wiring...")
    
    try:
        from src.ai_interviewer.controller import InterviewApplication
        from src.ai_interviewer.utils.config import Config
        from src.ai_interviewer.core.interview_graph import InterviewGraph
        
        # Verify Config
        if not Config.LANGGRAPH_ENABLED:
            logger.error("❌ LANGGRAPH_ENABLED is False! Test invalid.")
            return False
            
        # Initialize App
        app = InterviewApplication()
        
        # Verify Controller Type
        if isinstance(app.flow_controller, InterviewGraph):
            logger.info("✅ Controller initialized with InterviewGraph")
        else:
            logger.error(f"❌ Controller is {type(app.flow_controller)}, expected InterviewGraph")
            return False
            
        # Verify Interface Compatibility
        logger.info("🧪 Testing Interface Compatibility...")
        
        # 1. Start Interview
        result = app.start_topic_interview("Test Topic", "TestUser")
        
        # New API: Returns Dict
        if isinstance(result, dict) and result.get("success"):
            greeting = result.get("greeting", "").lower()
            if "welcome" in greeting or "let's begin" in greeting:
                 logger.info("✅ start_topic_interview successful")
            else:
                 logger.error(f"❌ start_topic_interview greeting unexpected: {greeting}")
                 return False
        else:
             logger.error(f"❌ start_topic_interview failed: {result}")
             return False
             
        # 2. Process Answer
        # Mock session setup (start_topic_interview sets up session in app)
        if not app.current_session:
             logger.error("❌ Session not initialized in app")
             return False
        
        result_ans = app.process_answer("Test Answer")
        
        # New API: Returns Dict
        if isinstance(result_ans, dict) and result_ans.get("success"):
             status = result_ans.get("status")
             if status in ["continue", "completed"]:
                 logger.info("✅ process_answer successful")
             else:
                 logger.warning(f"⚠️ process_answer status unexpected: {status}")
        else:
             logger.error(f"❌ process_answer failed: {result_ans}")
             
        logger.info("🎉 All Wiring Tests Passed!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import Error (Possible Circular Dependency): {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Runtime Error: {e}")
        return False

if __name__ == "__main__":
    test_wiring()
