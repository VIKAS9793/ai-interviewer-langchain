import os
import pytest
from unittest.mock import MagicMock, patch
from src.ai_interviewer.core.autonomous_flow_controller import AutonomousFlowController
from src.ai_interviewer.core.interview_graph import get_interview_graph

@pytest.fixture
def mock_clean_db():
    """Remove sqlite db before and after test"""
    if os.path.exists("interview_state.sqlite"):
        os.remove("interview_state.sqlite")
    yield
    # Cleanup is optional, maybe we want to inspect it?
    # if os.path.exists("interview_state.sqlite"):
    #     os.remove("interview_state.sqlite")

def test_persistence_wiring(mock_clean_db):
    """Verify Controller -> Graph -> Sqlite connection"""
    
    # 1. Instantiate Controller
    controller = AutonomousFlowController(model_name="test-model")
    
    # Verify it has the graph_engine
    assert hasattr(controller, "graph_engine")
    assert controller.graph_engine is get_interview_graph()
    
    # 2. Start Interview
    with patch("src.ai_interviewer.core.interview_graph.InterviewGraph.start_interview") as mock_start:
        mock_start.return_value = {
            "status": "started",
            "session_id": "test-session-123",
            "greeting": "Hello",
            "first_question": "Q1"
        }
        
        response = controller.start_interview("Python", "Tester")
        
        # Verify it delegated to the graph
        mock_start.assert_called_once()
        assert response["session_id"] == "test-session-123"

def test_sqlite_db_creation():
    """
    Verify that initializing the InterviewGraph creates the sqlite file connection.
    Note: SqliteSaver lazy loads or creates on write?
    The __init__ call: conn = sqlite3.connect("interview_state.sqlite") happens immediately.
    So file should exist after import/init.
    """
    if os.path.exists("interview_state.sqlite"):
        os.remove("interview_state.sqlite")
        
    # Re-import or Re-init to trigger __init__
    from src.ai_interviewer.core.interview_graph import InterviewGraph
    graph = InterviewGraph()
    
    # Check if file exists
    assert os.path.exists("interview_state.sqlite"), "Persistence DB file not created!"
    
    # Verify checkpointer type
    from langgraph.checkpoint.sqlite import SqliteSaver
    assert isinstance(graph.checkpointer, SqliteSaver)
