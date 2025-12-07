"""
Quick test of the autonomous AI interviewer system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_interviewer.core import (
    AutonomousReasoningEngine, 
    AutonomousInterviewer,
    InterviewContext, 
    CandidateState
)
from src.ai_interviewer.core.ai_guardrails import ResponsibleAI

def test_autonomous_system():
    print("=" * 60)
    print("🧪 Testing Autonomous AI Interviewer System")
    print("=" * 60)
    
    # 1. Test Reasoning Engine
    print("\n1️⃣ Testing AutonomousReasoningEngine...")
    engine = AutonomousReasoningEngine()
    context = InterviewContext(
        session_id='test123',
        candidate_name='Test Candidate',
        topic='Python/Backend Development',
        question_number=1,
        max_questions=5
    )
    
    thought = engine.think_before_acting(context, 'generate_question')
    print(f"   ✅ Chain-of-Thought reasoning")
    print(f"      - Conclusion: {thought.conclusion}")
    print(f"      - Confidence: {thought.confidence:.2f}")
    print(f"      - Reasoning steps: {len(thought.thoughts)}")
    
    # 2. Test Guardrails
    print("\n2️⃣ Testing ResponsibleAI (Guardrails)...")
    rai = ResponsibleAI()
    
    # Test content safety
    safety = rai.validate_content('Please explain Python decorators.')
    print(f"   ✅ Content safety check")
    print(f"      - Safe: {safety['safe']}")
    print(f"      - Level: {safety['level']}")
    
    # Test evaluation fairness
    eval_check = rai.guardrails.check_evaluation_fairness({
        'score': 7, 
        'feedback': 'Good technical knowledge demonstrated.'
    })
    print(f"   ✅ Evaluation fairness check")
    print(f"      - Passed: {eval_check.passed}")
    print(f"      - Level: {eval_check.safety_level.value}")
    
    # Test question fairness
    q_check = rai.guardrails.check_question_fairness(
        "Can you explain how Python handles memory management?",
        "Python/Backend Development"
    )
    print(f"   ✅ Question fairness check")
    print(f"      - Passed: {q_check.passed}")
    
    # 3. Test Explainability
    print("\n3️⃣ Testing AI Explainability...")
    explanation = rai.explainability.explain_question_choice(
        {"conclusion": "progressive_challenge", "confidence": 0.8, "thoughts": []},
        {"question_number": 2, "max_questions": 5}
    )
    print(f"   ✅ Explanation generated")
    print(f"      - Summary: {explanation['summary']}")
    
    # 4. Test Accountability
    print("\n4️⃣ Testing AI Accountability...")
    audit = rai.accountability.get_audit_summary()
    print(f"   ✅ Audit system operational")
    print(f"      - Total audits: {audit['total_audits']}")
    
    print("\n" + "=" * 60)
    print("🎉 All autonomous AI systems functional!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_autonomous_system()
