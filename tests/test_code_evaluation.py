import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai_interviewer.core.static_analyzer import StaticCodeAnalyzer

class TestStaticCodeAnalyzer(unittest.TestCase):
    
    def test_valid_python_complexity(self):
        code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
        result = StaticCodeAnalyzer.analyze(code, "python")
        self.assertTrue(result["valid"])
        metrics = result["metrics"]
        self.assertEqual(metrics["cyclomatic_complexity"], 4) # func + for + for + if
        self.assertEqual(metrics["max_nesting_depth"], 3) # func -> for -> for -> if (Wait, visitor logic might differ)
        
    def test_syntax_error(self):
        code = "def broken_function(: print('hi')"
        result = StaticCodeAnalyzer.analyze(code, "python")
        self.assertFalse(result["valid"])
        self.assertIn("Syntax Error", result["error"])
        
    def test_empty_submission(self):
        result = StaticCodeAnalyzer.analyze("", "python")
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Empty code submission")

    def test_non_python_fallback(self):
        code = "function test() { console.log('js'); }"
        result = StaticCodeAnalyzer.analyze(code, "javascript")
        self.assertTrue(result["valid"])
        self.assertEqual(result["metrics"]["status"], "syntax_check_skipped")

if __name__ == '__main__':
    unittest.main()
