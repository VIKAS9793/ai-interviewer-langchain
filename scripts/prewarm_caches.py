"""
Pre-warm Caches for Maximum Performance
Generates and caches common questions for instant responses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prewarm_caches():
    """Pre-warm all cache levels for maximum performance"""
    
    print("🔥 Pre-warming Caches for Maximum Performance")
    print("=" * 60)
    
    # Import components
    from src.ai_interviewer.core.speed_optimizer import get_speed_optimizer
    from src.ai_interviewer.core.offline_llm_engine import (
        OptimizedQuestionGenerator, 
        FastEvaluator,
        get_offline_llm
    )
    
    # Initialize components
    print("\n📦 Initializing components...")
    optimizer = get_speed_optimizer()
    llm_engine = get_offline_llm()
    question_gen = OptimizedQuestionGenerator(llm_engine)
    evaluator = FastEvaluator(llm_engine)
    
    print("   ✅ Components initialized")
    
    # Define topics and difficulties
    topics = [
        "JavaScript/Frontend Development",
        "Python/Backend Development",
        "Machine Learning/AI",
        "System Design",
        "Data Structures & Algorithms"
    ]
    
    difficulties = ["easy", "medium", "hard"]
    
    # Pre-generate questions
    print("\n📝 Pre-generating questions...")
    total_questions = 0
    start_time = time.time()
    
    for topic in topics:
        print(f"\n   Topic: {topic}")
        for difficulty in difficulties:
            for q_num in range(1, 6):  # 5 questions per difficulty
                # Generate question
                question = question_gen.generate_question(topic, difficulty, q_num)
                
                # Cache it
                cache_key = optimizer.cache_key(
                    "question",
                    topic=topic,
                    difficulty=difficulty,
                    question_number=q_num
                )
                
                _, time_ms, level = optimizer.get_or_generate(
                    key=cache_key,
                    generator=lambda q=question: q,
                    cache_type="questions",
                    ttl_hours=168  # 1 week
                )
                
                total_questions += 1
                print(f"      ✓ {difficulty.capitalize():8} Q{q_num}: {time_ms:.1f}ms ({level})")
    
    generation_time = time.time() - start_time
    print(f"\n   ✅ Generated and cached {total_questions} questions in {generation_time:.2f}s")
    
    # Pre-generate sample evaluations
    print("\n📊 Pre-generating sample evaluations...")
    
    sample_answers = {
        "excellent": "This is a comprehensive answer that demonstrates deep understanding of the concept. " +
                     "For example, when working with closures in JavaScript, we need to understand scope chains " +
                     "and lexical scoping. Here's a code example: function outer() { let x = 10; return function inner() " +
                     "{ return x; }; } This shows how inner functions can access outer scope variables.",
        
        "good": "The key concept here is understanding how scope works. Variables declared with let and const " +
                "are block-scoped, while var is function-scoped. This affects hoisting and availability.",
        
        "basic": "I think this relates to variable scope and how functions work in the language.",
        
        "poor": "Not sure."
    }
    
    total_evaluations = 0
    eval_start = time.time()
    
    for topic in topics[:2]:  # Just first 2 topics for samples
        for answer_type, answer_text in sample_answers.items():
            # Generate evaluation
            evaluation = evaluator.evaluate(
                question="Sample question for pre-warming",
                answer=answer_text,
                topic=topic
            )
            
            # Cache it
            cache_key = optimizer.cache_key(
                "evaluation",
                answer_hash=hash(answer_text),
                topic=topic
            )
            
            _, time_ms, level = optimizer.get_or_generate(
                key=cache_key,
                generator=lambda e=evaluation: e,
                cache_type="evaluations",
                ttl_hours=168
            )
            
            total_evaluations += 1
            print(f"   ✓ {answer_type.capitalize():10} answer: {time_ms:.1f}ms ({level})")
    
    eval_time = time.time() - eval_start
    print(f"\n   ✅ Generated and cached {total_evaluations} evaluations in {eval_time:.2f}s")
    
    # Pre-compute embeddings for common patterns
    print("\n🔤 Pre-computing embeddings...")
    
    common_phrases = [
        "explain the difference between",
        "how does",
        "what is",
        "describe",
        "implement",
        "design a system",
        "optimize",
        "what are the benefits",
        "when would you use",
        "compare and contrast"
    ]
    
    embedding_count = 0
    for phrase in common_phrases:
        embedding = llm_engine._get_embedding_model().encode(phrase)
        embedding_count += 1
    
    print(f"   ✅ Pre-computed {embedding_count} embeddings")
    
    # Show final statistics
    print("\n" + "=" * 60)
    print("✅ CACHE PRE-WARMING COMPLETE!")
    print("=" * 60)
    
    metrics = optimizer.get_metrics()
    
    print(f"\n📊 Cache Statistics:")
    print(f"   L1 Cache: {metrics['l1_stats']['size']}/{metrics['l1_stats']['max_size']} items")
    print(f"   L2 Cache: {metrics['l2_stats']['size']}/{metrics['l2_stats']['max_size']} items")
    print(f"   Overall Hit Rate: {metrics['overall_hit_rate']:.1%}")
    
    print(f"\n⚡ Performance:")
    print(f"   L1 Avg Time: {metrics['avg_l1_time_ms']:.1f}ms")
    print(f"   L2 Avg Time: {metrics['avg_l2_time_ms']:.1f}ms")
    
    print(f"\n🎯 Results:")
    print(f"   Total Questions Cached: {total_questions}")
    print(f"   Total Evaluations Cached: {total_evaluations}")
    print(f"   Total Time: {generation_time + eval_time:.2f}s")
    
    print("\n💡 Next Steps:")
    print("   1. Start application: python enhanced_main.py")
    print("   2. First questions will be instant (<50ms)")
    print("   3. Cache automatically maintained and refreshed")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        prewarm_caches()
    except Exception as e:
        print(f"\n❌ Error pre-warming caches: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
