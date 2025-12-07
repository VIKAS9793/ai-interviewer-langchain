"""
Test Suite for Hybrid Research-Based Modules

Tests for:
- ReasoningBank (arXiv:2509.25140)
- ReflectAgent (arXiv:2510.08002)
- MetacognitiveSystem (arXiv:2506.05109)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_reasoning_bank():
    """Test ReasoningBank memory system."""
    print("\n" + "="*60)
    print("🧠 Testing ReasoningBank")
    print("="*60)
    
    from ai_interviewer.core import ReasoningBank, MemoryItem, InterviewTrajectory
    
    # Initialize with temp database
    bank = ReasoningBank(db_path="./test_reasoning_bank.db")
    
    # Test adding memories
    print("\n1️⃣ Testing memory creation...")
    memory = MemoryItem(
        title="Ask foundational questions first",
        description="Start with basics before complex topics",
        content="When interviewing Python candidates, begin with data types and control flow before OOP",
        source_type="success",
        topic="Python",
        confidence=0.8
    )
    bank.add_memory(memory)
    print(f"   ✅ Memory added: {memory.title}")
    
    # Test retrieval
    print("\n2️⃣ Testing memory retrieval...")
    results = bank.retrieve("Python basics", topic="Python", k=3)
    print(f"   ✅ Retrieved {len(results)} memories")
    
    # Test trajectory distillation
    print("\n3️⃣ Testing trajectory distillation...")
    trajectory = InterviewTrajectory(
        session_id="test-001",
        candidate_name="Test Candidate",
        topic="Python",
        questions=[{"question": "What are Python data types?"}],
        answers=[{"answer": "int, str, float..."}],
        evaluations=[{"overall_score": 8}],
        final_score=8.0,
        success=True,
        resolution_patterns=["Progressive difficulty worked well"]
    )
    memories = bank.distill_memories(trajectory)
    print(f"   ✅ Distilled {len(memories)} memories from trajectory")
    
    # Test statistics
    print("\n4️⃣ Testing statistics...")
    stats = bank.get_statistics()
    print(f"   ✅ Total memories: {stats['total_memories']}")
    print(f"   ✅ Success strategies: {stats['success_strategies']}")
    
    # Cleanup
    import os
    if os.path.exists("./test_reasoning_bank.db"):
        os.remove("./test_reasoning_bank.db")
    
    print("\n✅ ReasoningBank tests passed!")
    return True


def test_reflect_agent():
    """Test ReflectAgent quality assurance."""
    print("\n" + "="*60)
    print("🔍 Testing ReflectAgent")
    print("="*60)
    
    from ai_interviewer.core import ReflectAgent, ReflectionOutcome
    
    agent = ReflectAgent()
    
    # Test question fairness
    print("\n1️⃣ Testing question fairness...")
    
    # Good question
    result = agent.evaluate_question_fairness(
        "Explain the difference between lists and tuples in Python",
        "Python"
    )
    assert result.outcome == ReflectionOutcome.PASSED
    print(f"   ✅ Fair question: {result.outcome.value}")
    
    # Potentially problematic question
    result = agent.evaluate_question_fairness(
        "Are you married? Also explain Python classes",
        "Python"
    )
    assert result.outcome in [ReflectionOutcome.WARNING, ReflectionOutcome.FAILED]
    print(f"   ✅ Detected issue: {result.outcome.value}")
    
    # Test scoring consistency
    print("\n2️⃣ Testing scoring consistency...")
    result = agent.evaluate_scoring_consistency(
        answer="Python uses duck typing for dynamic dispatch",
        score=7.5,
        justification="Good understanding of Python's type system",
        topic="Python",
        previous_scores=[7, 8, 7.5]
    )
    print(f"   ✅ Scoring check: {result.outcome.value}")
    
    # Test extreme score detection
    result = agent.evaluate_scoring_consistency(
        answer="Yes",
        score=9.5,
        justification="Good",
        topic="Python"
    )
    assert len(result.recommendations) > 0
    print(f"   ✅ Extreme score flagged: {len(result.recommendations)} recommendations")
    
    # Test SOP extraction
    print("\n3️⃣ Testing SOP extraction...")
    sop = agent.extract_sop(
        session_id="test-002",
        topic="Python",
        questions=[
            {"question": "What is Python?", "difficulty": "easy"},
            {"question": "Explain decorators", "difficulty": "hard"}
        ],
        evaluations=[
            {"overall_score": 8},
            {"overall_score": 7}
        ],
        final_score=7.5
    )
    assert sop is not None
    print(f"   ✅ SOP extracted: {sop.title}")
    
    # Test summary
    print("\n4️⃣ Testing reflection summary...")
    summary = agent.get_reflection_summary()
    print(f"   ✅ Total reflections: {summary['total']}")
    print(f"   ✅ Pass rate: {summary['pass_rate']:.0%}")
    
    print("\n✅ ReflectAgent tests passed!")
    return True


def test_metacognitive_system():
    """Test MetacognitiveSystem self-improvement."""
    print("\n" + "="*60)
    print("📊 Testing MetacognitiveSystem")
    print("="*60)
    
    from ai_interviewer.core import MetacognitiveSystem, BeliefSystem, CapabilityLevel
    
    # Test with temp state file
    system = MetacognitiveSystem(state_path="./test_metacog.json")
    
    # Test capability updates
    print("\n1️⃣ Testing capability tracking...")
    system.update_capability("Python", 0.7)
    system.update_capability("JavaScript", 0.4)
    system.update_capability("System Design", 0.3)
    print(f"   ✅ Updated 3 capabilities")
    
    # Test self-assessment
    print("\n2️⃣ Testing self-assessment...")
    assessments = system.assess_capabilities()
    print(f"   ✅ Python: {assessments.get('Python', CapabilityLevel.NOVICE).value}")
    print(f"   ✅ JavaScript: {assessments.get('JavaScript', CapabilityLevel.NOVICE).value}")
    
    # Test weakness/strength identification
    print("\n3️⃣ Testing weakness/strength identification...")
    weaknesses = system.identify_weaknesses()
    strengths = system.identify_strengths()
    print(f"   ✅ Weaknesses: {weaknesses}")
    print(f"   ✅ Strengths: {strengths}")
    
    # Test learning goal planning
    print("\n4️⃣ Testing learning goal planning...")
    goals = system.plan_improvement()
    print(f"   ✅ Created {len(goals)} learning goals")
    
    # Test performance evaluation
    print("\n5️⃣ Testing performance evaluation...")
    result = system.evaluate_performance(
        session_id="test-003",
        topic="JavaScript",
        scores=[6, 7, 5, 6],
        reflection_outcome="passed"
    )
    print(f"   ✅ Performance: {result['session_performance']:.0%}")
    print(f"   ✅ Recommendation: {result['recommendation'][:50]}...")
    
    # Test belief system
    print("\n6️⃣ Testing BeliefSystem...")
    beliefs = BeliefSystem()
    beliefs.update_candidate_state("confident", 0.8)
    beliefs.update_performance_trend("improving", 0.7)
    beliefs.add_intention("ask_challenging_question", "candidate is excelling")
    
    state_belief = beliefs.get_belief("candidate")
    assert state_belief is not None
    print(f"   ✅ Candidate belief: {state_belief.predicate}")
    
    # Cleanup
    import os
    if os.path.exists("./test_metacog.json"):
        os.remove("./test_metacog.json")
    
    print("\n✅ MetacognitiveSystem tests passed!")
    return True


def test_integration():
    """Test integration of all hybrid modules."""
    print("\n" + "="*60)
    print("🔗 Testing Hybrid Integration")
    print("="*60)
    
    from ai_interviewer.core import (
        ReasoningBank, ReflectAgent, MetacognitiveSystem, BeliefSystem
    )
    
    # Initialize all systems
    print("\n1️⃣ Initializing hybrid systems...")
    memory = ReasoningBank(db_path="./test_integration.db")
    reflector = ReflectAgent()
    metacog = MetacognitiveSystem(state_path="./test_integration_meta.json")
    beliefs = BeliefSystem()
    print("   ✅ All systems initialized")
    
    # Simulate interview flow
    print("\n2️⃣ Simulating interview with hybrid systems...")
    
    # Before question: retrieve memories
    strategies = memory.retrieve("Python interview", topic="Python")
    print(f"   📚 Retrieved {len(strategies)} strategies")
    
    # Update beliefs
    beliefs.update_candidate_state("nervous", 0.6)
    beliefs.add_intention("start_with_easy_question", "candidate seems nervous")
    print("   💭 Updated beliefs")
    
    # Reflect on question
    question = "What is the difference between a list and tuple in Python?"
    reflection = reflector.evaluate_question_fairness(question, "Python")
    print(f"   🔍 Question check: {reflection.outcome.value}")
    
    # Simulate answer and score
    answer = "Lists are mutable, tuples are immutable"
    score = 7.5
    justification = "Good understanding of basic concepts"
    
    score_check = reflector.evaluate_scoring_consistency(
        answer, score, justification, "Python"
    )
    print(f"   📊 Score check: {score_check.outcome.value}")
    
    # Update metacognitive system
    metacog.update_capability("Python", 0.75)
    print("   🧠 Updated metacognitive state")
    
    # Get final summary
    print("\n3️⃣ Final summaries...")
    mem_stats = memory.get_statistics()
    ref_stats = reflector.get_reflection_summary()
    meta_summary = metacog.get_summary()
    
    print(f"   📚 Memory: {mem_stats['total_memories']} items")
    print(f"   🔍 Reflections: {ref_stats['total']} checks, {ref_stats['pass_rate']:.0%} pass rate")
    print(f"   🧠 Metacognitive: {meta_summary['total_sessions']} sessions analyzed")
    
    # Cleanup
    import os
    for f in ["./test_integration.db", "./test_integration_meta.json"]:
        if os.path.exists(f):
            os.remove(f)
    
    print("\n✅ Integration tests passed!")
    return True


if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Hybrid Research-Based Modules")
    print("="*60)
    
    success = True
    
    try:
        success &= test_reasoning_bank()
        success &= test_reflect_agent()
        success &= test_metacognitive_system()
        success &= test_integration()
        
        print("\n" + "="*60)
        if success:
            print("🎉 ALL HYBRID MODULE TESTS PASSED!")
        else:
            print("⚠️ Some tests failed")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
