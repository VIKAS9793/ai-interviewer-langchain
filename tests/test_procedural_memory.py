
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Fix imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking specific persistent interactions in logic, not the module import itself
# sys.modules["huggingface_hub"] = MagicMock() 
# sys.modules["huggingface_hub.utils"] = MagicMock()

from src.ai_interviewer.modules.learning_service import ReasoningBank, SkillModule, MemoryItem, InterviewTrajectory
from src.ai_interviewer.core.autonomous_reasoning_engine import AutonomousReasoningEngine, InterviewContext, CandidateState

class TestProceduralMemory(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "test_reasoning_bank.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        self.reasoning_bank = ReasoningBank(db_path=self.test_db)
        self.reasoning_bank.persistence = MagicMock() # Mock persistence
        
        self.engine = AutonomousReasoningEngine()
        self.engine.reasoning_bank = self.reasoning_bank

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass # Windows file lock sometimes lags
        
    def test_skill_module_serialization(self):
        """Test SkillModule -> MemoryItem conversion"""
        skill = SkillModule(
            skill_id="skill_123",
            trigger_context="candidate_struggling_python",
            action_chain=["simplify_question", "provide_hint"],
            success_rate=0.85
        )
        
        memory_item = skill.to_memory_item()
        self.assertEqual(memory_item.title, "[SKILL] candidate_struggling_python")
        self.assertEqual(memory_item.source_type, "skill_module")
        self.assertIn("simplify_question", memory_item.content)
        print("✅ SkillModule serialization passed")

    def test_reasoning_engine_skill_injection(self):
        """Test if Engine includes learned skills in options"""
        
        # 1. Mock Retrieval
        mock_skill = MemoryItem(
            title="[SKILL] Python Advanced",
            description="Use deep dive for experts",
            content="['ask_internals', 'check_memory_management']",
            source_type="skill_module",
            topic="python",
            confidence=0.9
        )
        self.reasoning_bank.retrieve = MagicMock(return_value=[mock_skill])
        
        # 2. Setup Context
        context = InterviewContext(
            session_id="test_sess",
            candidate_name="Test User",
            topic="python",
            question_number=1,
            max_questions=5,
            candidate_state=CandidateState.EXCELLING
        )
        
        # 3. Execute Option Generation (Directly)
        options = self.engine._generate_options(
            context, 
            "generate_question", 
            {"performance_trend": "stable", "knowledge_profile": {"gaps": []}, "candidate_state": "excelling"},
            learned_skills=[mock_skill]
        )
        
        # 4. Verify Injection
        skill_option = next((o for o in options if "learned_skill" in o["approach"]), None)
        self.assertIsNotNone(skill_option)
        self.assertEqual(skill_option["source"], "procedural_memory")
        self.assertGreater(skill_option["suitability"], 0.9)
        print("✅ Learned Skill injection passed")

    def test_persistence_sync_trigger(self):
        """Test if distill_memories triggers cloud sync"""
        
        # Create a dummy trajectory
        traj = InterviewTrajectory(
            session_id="sess_1",
            candidate_name="Bob",
            topic="Java",
            questions=[],
            answers=[],
            evaluations=[],
            final_score=8.0,
            success=True,
            resolution_patterns=["Pattern A"]
        )
        
        # Mock extraction to return at least one memory
        self.reasoning_bank._extract_success_strategies = MagicMock(return_value=[
            MemoryItem("Strat 1", "Desc", "Content", "success")
        ])
        
        self.reasoning_bank.distill_memories(traj)
        
        # Verify sync called
        self.reasoning_bank.persistence.sync_up.assert_called()
        print("✅ Cloud Sync triggered successfully")

if __name__ == '__main__':
    unittest.main()
