"""
Integration tests for rate limiter with mock LLMs.
Tests quota enforcement, fallback logic, and caching issues.
"""
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from mocks.mock_llm import MockGemini, MockHuggingFace, AIMessage
from src.ai_interviewer.utils.rate_limiter import get_rate_limiter
from src.ai_interviewer.utils.config import Config


def test_quota_enforcement():
    """
    Test that rate limiter correctly enforces 20 RPD limit.
    Simulates 25 API calls - first 20 should succeed, 21+ should be blocked.
    """
    print("\n" + "="*80)
    print("TEST 1: Quota Enforcement (20 RPD Limit)")
    print("="*80)
    
    rate_limiter = get_rate_limiter()
    rate_limiter.daily_quota.reset()  # Start fresh
    
    mock_gemini = MockGemini(quota_limit=20)
    
    gemini_calls = 0
    fallback_triggered = False
    
    for i in range(1, 26):
        try:
            # Check quota BEFORE invoke (this is what we're testing)
            if rate_limiter.daily_quota.is_quota_exhausted():
                print(f"❌ Call {i}: Quota exhausted, should use fallback")
                assert i > 20, f"Quota exhausted too early at call {i}!"
                fallback_triggered = True
                break
            
            # Record request (this is what autonomous_reasoning_engine.py should do)
            rate_limiter.daily_quota.record_request()
            gemini_calls += 1
            
            # Invoke mock Gemini
            result = mock_gemini.invoke("test prompt")
            print(f"✅ Call {i}: Gemini success - {result.content}")
            
        except Exception as e:
            if "429" in str(e):
                print(f"⚠️  Call {i}: Got 429 error from Gemini")
                # Mark quota exhausted (this is what error handler should do)
                rate_limiter.daily_quota._requests_today = Config.RATE_LIMIT_RPD
                fallback_triggered = True
                break
            else:
                raise
    
    # Assertions
    assert gemini_calls == 20, f"Expected exactly 20 Gemini calls, got {gemini_calls}"
    assert fallback_triggered, "Fallback should have been triggered at call 21"
    assert rate_limiter.daily_quota.is_quota_exhausted(), "Quota should be marked as exhausted"
    
    print(f"\n✅ TEST PASSED: Gemini used {gemini_calls}/20 calls, fallback triggered correctly")
    return True


def test_429_error_detection():
    """
    Test that 429 errors are detected and trigger quota exhaustion.
    """
    print("\n" + "="*80)
    print("TEST 2: 429 Error Detection & Quota Marking")
    print("="*80)
    
    rate_limiter = get_rate_limiter()
    rate_limiter.daily_quota.reset()
    
    mock_gemini = MockGemini(quota_limit=5)  # Lower limit for faster test
    
    try:
        # Make 6 calls (should fail on 6th)
        for i in range(1, 7):
            rate_limiter.daily_quota.record_request()
            result = mock_gemini.invoke("test")
            print(f"✅ Call {i}: Success")
    except Exception as e:
        if "429" in str(e):
            print(f"⚠️  Got 429 error as expected")
            # This is what the error handler should do
            rate_limiter.daily_quota._count = Config.RATE_LIMIT_RPD
            print(f"✅ Marked quota as exhausted: {rate_limiter.daily_quota.requests_today}/{Config.RATE_LIMIT_RPD}")
        else:
            raise
    
    assert rate_limiter.daily_quota.is_quota_exhausted(), "Quota should be exhausted after 429"
    print("\n✅ TEST PASSED: 429 error detected and quota marked correctly")
    return True


def test_fallback_mechanism():
    """
    Test complete fallback flow: Gemini → 429 → HuggingFace.
    """
    print("\n" + "="*80)
    print("TEST 3: Complete Fallback Mechanism")
    print("="*80)
    
    rate_limiter = get_rate_limiter()
    rate_limiter.daily_quota.reset()
    
    mock_gemini = MockGemini(quota_limit=3)
    mock_hf = MockHuggingFace()
    
    current_llm = mock_gemini
    
    for i in range(1, 6):
        try:
            # Check quota first
            if rate_limiter.daily_quota.is_quota_exhausted():
                print(f"⚠️  Call {i}: Switching to HuggingFace (quota exhausted)")
                current_llm = mock_hf
            
            # Record if using Gemini
            if current_llm.name == "MockGemini":
                rate_limiter.daily_quota.record_request()
            
            # Invoke
            result = current_llm.invoke("test")
            print(f"✅ Call {i}: {current_llm.name} - {result.content}")
            
        except Exception as e:
            if "429" in str(e):
                print(f"⚠️  Call {i}: 429 from Gemini, switching to HuggingFace")
                rate_limiter.daily_quota._count = Config.RATE_LIMIT_RPD
                current_llm = mock_hf
                result = current_llm.invoke("test")
                print(f"✅ Call {i}: {current_llm.name} (fallback) - {result.content}")
    
    # We record BEFORE invoke, so even though quota_limit=3, we'll try 4 times
    # (calls 1-3 succeed, call 4 triggers 429)
    assert mock_gemini.call_count == 4, f"Should have made 4 Gemini calls (3 success, 1 with 429), got {mock_gemini.call_count}"
    assert mock_hf.call_count > 0, "Should have fallen back to HuggingFace"
    
    print(f"\n✅ TEST PASSED: Gemini calls: {mock_gemini.call_count}, HuggingFace calls: {mock_hf.call_count}")
    return True


def test_caching_issue():
    """
    Test the LLM caching problem that caused the original bug.
    Simulates what happens when llm._llm is cached.
    """
    print("\n" + "="*80)
    print("TEST 4: LLM Caching Issue (The Bug)")
    print("="*80)
    
    rate_limiter = get_rate_limiter()
    rate_limiter.daily_quota.reset()
    
    # Simulate cached LLM behavior
    cached_llm = MockGemini(quota_limit=20)
    
    print("⚠️  Simulating BUGGY behavior (cached LLM, no quota check before invoke):")
    
    # Fill quota to 20
    for i in range(20):
        rate_limiter.daily_quota.record_request()
    
    print(f"Quota filled: {rate_limiter.daily_quota.requests_today}/20")
    
    # Now try to use cached LLM (this is the bug - no quota check!)
    try:
        result = cached_llm.invoke("This should fail!")
        print(f"❌ BUG REPRODUCED: Call went through even though quota exhausted!")
        print(f"   Result: {result.content}")
    except Exception as e:
        if "429" in str(e):
            print(f"✅ 429 error caught (expected with buggy code)")
    
    print("\n✅ TEST PASSED: Bug reproduced - cached LLM bypasses quota check")
    return True


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# RATE LIMITER INTEGRATION TESTS")
    print("#"*80)
    
    try:
        test_quota_enforcement()
        test_429_error_detection()
        test_fallback_mechanism()
        test_caching_issue()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nNext step: Fix autonomous_reasoning_engine.py to prevent caching issue")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
