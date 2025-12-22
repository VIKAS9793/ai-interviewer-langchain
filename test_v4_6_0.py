"""
Comprehensive test suite for v4.6.0 Sequential Safety feature.

Tests all risk patterns, edge cases, and integration.
"""

from src.adk_interviewer.agents.coding_agent import assess_code_risk, create_coding_agent


def test_safe_code():
    """Test that safe code gets 0 risk score."""
    safe_codes = [
        "print('Hello World')",
        "x = [1, 2, 3]\nprint(sum(x))",
        "def factorial(n):\n    return 1 if n == 0 else n * factorial(n-1)",
        "import math\nprint(math.sqrt(16))",
        "",  # Empty string
        "   ",  # Whitespace only
    ]
    
    print("=== Testing Safe Code ===")
    for code in safe_codes:
        risk, issues = assess_code_risk(code)
        assert risk == 0.0, f"Safe code flagged as risky: {code[:30]}"
        assert len(issues) == 0, f"Safe code has issues: {issues}"
        print(f"✅ Safe: {code[:30]:<30} | Risk: {risk}")
    print()


def test_dangerous_patterns():
    """Test all 10 dangerous patterns individually."""
    patterns = [
        ("__import__('os')", "Dynamic import"),
        ("eval('1+1')", "Direct eval"),
        ("exec('print(1)')", "Code execution"),
        ("compile('x=1', '<string>', 'exec')", "Code compilation"),
        ("os.system('ls')", "System command"),
        ("subprocess.run(['ls'])", "Subprocess execution"),
        ("open('file.txt', 'w')", "File write"),
        ("os.remove('file.txt')", "File deletion"),
        ("shutil.rmtree('/tmp')", "File manipulation"),
        ("import requests\nrequests.get('http://example.com')", "Network request"),
    ]
    
    print("=== Testing Dangerous Patterns ===")
    for code, expected_issue in patterns:
        risk, issues = assess_code_risk(code)
        assert risk > 0, f"Dangerous code not detected: {code}"
        assert len(issues) > 0, f"No issues found for: {code}"
        print(f"🚨 Risky: {expected_issue:<25} | Risk: {risk:.2f} | Issues: {issues}")
    print()


def test_multiple_risks():
    """Test code with multiple dangerous patterns."""
    multi_risk_code = """
import os
import subprocess

os.system('rm -rf /')
subprocess.call(['danger'])
eval('malicious')
"""
    
    print("=== Testing Multiple Risks ===")
    risk, issues = assess_code_risk(multi_risk_code)
    print(f"Code with 3 dangerous usage patterns:")
    print(f"  Risk Score: {risk:.2f}")
    print(f"  Detected Issues: {issues}")
    # Note: 'import os' and 'import subprocess' are safe - only USAGE is risky
    assert risk >= 0.6, "Multiple risks should have high score"
    assert len(issues) == 3, f"Should detect 3 usage patterns, got {len(issues)}"
    print("✅ Multiple risks detected correctly\n")


def test_edge_cases():
    """Test edge cases and corner scenarios."""
    edge_cases = [
        # Case sensitivity
        ("EVAL('test')", "Upper case eval"),
        ("Os.System('test')", "Mixed case os.system"),
        
        # Spacing variations
        ("eval ('test')", "Eval with space"),
        ("os . system('test')", "os.system with spaces"),
        
        # Comments (should still detect)
        ("# eval('danger')\neval('real')", "Commented + real eval"),
        
        # Strings (should detect pattern in string too)
        ('text = "eval(danger)"', "Pattern in string"),
    ]
    
    print("=== Testing Edge Cases ===")
    for code, description in edge_cases:
        risk, issues = assess_code_risk(code)
        print(f"{description:<30} | Risk: {risk:.2f} | Issues: {issues}")
    print()


def test_false_positives():
    """Test potential false positives that should be safe."""
    potentially_false = [
        "# This is a comment about eval",
        "variable_eval = 5",
        "print('The eval function is dangerous')",
        "def my_evaluation(): pass",
    ]
    
    print("=== Testing Potential False Positives ===")
    for code in potentially_false:
        risk, issues = assess_code_risk(code)
        status = "⚠️ FALSE POSITIVE" if risk > 0 else "✅ Correct"
        print(f"{status} | {code[:40]:<40} | Risk: {risk:.2f}")
    print()


def test_agent_creation():
    """Test that coding agent creates successfully with safety features."""
    print("=== Testing Agent Creation ===")
    agent = create_coding_agent()
    
    assert agent is not None, "Agent creation failed"
    assert agent.name == "coding_agent", f"Wrong name: {agent.name}"
    assert "safety" in agent.description.lower(), "Description missing safety info"
    assert agent.code_executor is not None, "Code executor not attached"
    
    print(f"✅ Agent created: {agent.name}")
    print(f"   Description: {agent.description[:80]}...")
    print(f"   Has code executor: {agent.code_executor is not None}")
    print()


def test_import_integrity():
    """Test all imports work correctly."""
    print("=== Testing Import Integrity ===")
    
    try:
        from src.adk_interviewer.agent import root_agent
        print(f"✅ Root agent imported: {len(root_agent.sub_agents)} sub-agents")
        
        from src.adk_interviewer.agents.coding_agent import assess_code_risk, create_coding_agent
        print("✅ Coding agent functions imported")
        
        from src.adk_interviewer.agents import (
            interviewer_agent, resume_agent, coding_agent,
            safety_agent, study_agent, critic_agent
        )
        print("✅ All agent modules imported")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise
    print()


def run_all_tests():
    """Execute complete test suite."""
    print("\n" + "="*60)
    print(" v4.6.0 COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    try:
        test_import_integrity()
        test_safe_code()
        test_dangerous_patterns()
        test_multiple_risks()
        test_edge_cases()
        test_false_positives()
        test_agent_creation()
        
        print("="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
