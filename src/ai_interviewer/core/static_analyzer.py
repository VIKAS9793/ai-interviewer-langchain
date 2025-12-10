import ast
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ComplexityVisitor(ast.NodeVisitor):
    """
    AST Visitor to estimate cyclomatic complexity and nesting depth.
    Helper for identifying potentially inefficient code (O(n^2)+).
    """
    def __init__(self):
        self.complexity = 1
        self.max_nesting = 0
        self.current_nesting = 0

    def visit_If(self, node):
        self.complexity += 1
        self._visit_nesting(node)

    def visit_For(self, node):
        self.complexity += 1
        self._visit_nesting(node)

    def visit_While(self, node):
        self.complexity += 1
        self._visit_nesting(node)

    def visit_FunctionDef(self, node):
        # Don't increment complexity for function def itself, just reset nesting
        old_nesting = self.current_nesting
        self.current_nesting = 0
        self.generic_visit(node)
        self.current_nesting = old_nesting

    def _visit_nesting(self, node):
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1

class StaticCodeAnalyzer:
    """
    Safe static analysis for code evaluation.
    Verifies syntax and estimates complexity without execution.
    """
    
    @staticmethod
    def analyze(code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code for syntax errors and structural metrics.
        Returns dictionary with 'valid', 'error', 'metrics'.
        """
        if not code or not code.strip():
            return {"valid": False, "error": "Empty code submission"}
            
        if language.lower() == "python":
            return StaticCodeAnalyzer._analyze_python(code)
        
        # MVP: Basic check for other languages
        if len(code) > 10000:
             return {"valid": False, "error": "Code too long (>10k chars)"}
             
        return {
            "valid": True,
            "error": None, 
            "metrics": {"language": language, "status": "syntax_check_skipped"}
        }

    @staticmethod
    def _analyze_python(code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
            
            # Analyze complexity
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            return {
                "valid": True,
                "error": None,
                "metrics": {
                    "cyclomatic_complexity": visitor.complexity,
                    "max_nesting_depth": visitor.max_nesting,
                    "loc": len(code.splitlines())
                },
                "ast_parsed": True
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax Error on line {e.lineno}: {e.msg}",
                "line": e.lineno
            }
        except Exception as e:
            logger.error(f"Static analysis failed: {e}")
            return {"valid": False, "error": f"Analysis Error: {str(e)}"}
