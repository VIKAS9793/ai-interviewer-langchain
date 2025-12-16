"""
Integration Test: Simulate 10-question interview to verify no semantic duplicates.

This test simulates the actual question generation flow to verify
the semantic deduplication fix works end-to-end.
"""

import logging
from src.ai_interviewer.modules.semantic_dedup import SemanticDeduplicator, get_deduplicator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_interview_questions():
    """
    Simulate generating 10 interview questions and verify no duplicates.
    
    Uses a mix of:
    1. Topic-based questions
    2. Experience-based questions  
    3. Challenge/problem questions
    
    The deduplicator should block semantic duplicates.
    """
    print("\n" + "="*60)
    print("INTEGRATION TEST: 10-Question Interview Simulation")
    print("="*60 + "\n")
    
    dedup = get_deduplicator(threshold=0.70)
    
    # Simulate questions that might be generated
    test_questions = [
        # Round 1: Should all pass (unique)
        "What is your experience with Python programming?",
        "How do you handle database optimization in large-scale systems?",
        "Explain the difference between REST and GraphQL APIs",
        "Describe your approach to writing unit tests",
        "What design patterns have you used in production?",
        
        # Round 2: Some should be blocked as semantic duplicates
        "Tell me about your Python experience",  # Duplicate of Q1
        "How do you optimize database queries?",  # Similar to Q2
        "What testing strategies do you follow?",  # Similar to Q4
        "Explain RESTful API design principles",  # Similar to Q3
        "What is your experience with software design patterns?",  # Similar to Q5
    ]
    
    question_history = []
    blocked_count = 0
    allowed_count = 0
    
    print("Simulating question generation...\n")
    
    for i, question in enumerate(test_questions, 1):
        is_duplicate, score = dedup.is_duplicate(
            question, 
            question_history, 
            return_score=True
        )
        
        if is_duplicate:
            status = "❌ BLOCKED"
            blocked_count += 1
        else:
            status = "✅ ALLOWED"
            allowed_count += 1
            question_history.append(question)
        
        print(f"Q{i:2d} [{status}] (score: {score:.3f})")
        print(f"    \"{question[:60]}...\"")
        print()
    
    print("="*60)
    print(f"RESULTS: {allowed_count} allowed, {blocked_count} blocked")
    print(f"Questions in history: {len(question_history)}")
    print("="*60)
    
    # Verification
    print("\n📋 Final Question Set (no duplicates):")
    for i, q in enumerate(question_history, 1):
        print(f"  {i}. {q[:70]}...")
    
    # Success criteria - at least 1 duplicate should be blocked
    print("\n🎯 SUCCESS CRITERIA:")
    print(f"  - At least 1 semantic duplicate blocked: ", end="")
    if blocked_count >= 1:
        print("✅ PASSED")
    else:
        print(f"⚠️ No duplicates blocked (expected at least 1)")
    
    print(f"  - No semantic duplicates in final set: ", end="")
    # Check final set for duplicates
    final_duplicates = 0
    for i, q1 in enumerate(question_history):
        for j, q2 in enumerate(question_history):
            if i < j:
                is_dup, score = dedup.is_duplicate(q1, [q2], return_score=True)
                if is_dup:
                    final_duplicates += 1
                    print(f"\n    ⚠️ Potential duplicate: Q{i+1} and Q{j+1} (score: {score:.3f})")
    
    if final_duplicates == 0:
        print("✅ PASSED")
    else:
        print(f"❌ FAILED - {final_duplicates} duplicates found")
    
    return blocked_count >= 1 and final_duplicates == 0


if __name__ == "__main__":
    success = simulate_interview_questions()
    print(f"\n{'='*60}")
    print(f"OVERALL: {'✅ INTEGRATION TEST PASSED' if success else '❌ INTEGRATION TEST FAILED'}")
    print(f"{'='*60}")
    exit(0 if success else 1)
