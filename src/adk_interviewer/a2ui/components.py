"""
A2UI Component Schemas for AI Interviewer.

Defines the UI components that agents can render:
- CodeEditor: For code display and editing
- QuestionCard: For interview questions
- FeedbackPanel: For scoring/feedback
"""

import json
from typing import Any

# A2UI Base Schema (simplified from official spec)
A2UI_SCHEMA = """
{
  "type": "object",
  "required": ["type", "id"],
  "properties": {
    "type": { "type": "string" },
    "id": { "type": "string" },
    "properties": { "type": "object" },
    "children": { 
      "type": "array",
      "items": { "$ref": "#" }
    }
  }
}
"""

# Interview-specific UI components
INTERVIEW_UI_COMPONENTS = {
    "code-editor": {
        "description": "Code editor with syntax highlighting",
        "properties": {
            "code": "string - The code content",
            "language": "string - Programming language (python, javascript, etc.)",
            "readonly": "boolean - Whether the editor is read-only",
            "lineNumbers": "boolean - Show line numbers"
        },
        "example": {
            "type": "code-editor",
            "id": "code-1",
            "properties": {
                "code": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)",
                "language": "python",
                "readonly": True,
                "lineNumbers": True
            }
        }
    },
    "question-card": {
        "description": "Interview question display",
        "properties": {
            "title": "string - Question title",
            "difficulty": "string - easy/medium/hard",
            "timeLimit": "number - Time limit in minutes",
            "description": "string - Full question text",
            "tags": "array - Topic tags"
        },
        "example": {
            "type": "question-card",
            "id": "question-1",
            "properties": {
                "title": "Two Sum",
                "difficulty": "easy",
                "timeLimit": 15,
                "description": "Given an array of integers nums and an integer target...",
                "tags": ["arrays", "hash-table"]
            }
        }
    },
    "feedback-panel": {
        "description": "Scoring and feedback display",
        "properties": {
            "score": "number - Score out of 10",
            "feedback": "string - Detailed feedback",
            "strengths": "array - List of strengths",
            "improvements": "array - Areas to improve"
        },
        "example": {
            "type": "feedback-panel",
            "id": "feedback-1",
            "properties": {
                "score": 8.5,
                "feedback": "Good solution with optimal time complexity.",
                "strengths": ["Clean code", "Proper edge case handling"],
                "improvements": ["Could add more comments"]
            }
        }
    },
    "hint-box": {
        "description": "Progressive hints for study mode",
        "properties": {
            "level": "number - Hint level (1-3)",
            "content": "string - Hint content",
            "revealed": "boolean - Whether hint is shown"
        },
        "example": {
            "type": "hint-box",
            "id": "hint-1",
            "properties": {
                "level": 1,
                "content": "Think about using a hash map for O(1) lookups.",
                "revealed": False
            }
        }
    }
}


def get_a2ui_prompt() -> str:
    """Generate A2UI prompt instructions for agents."""
    components_doc = json.dumps(INTERVIEW_UI_COMPONENTS, indent=2)
    
    return f"""
## A2UI Response Format (v4.7 Experimental)

When providing responses that would benefit from rich UI, you MAY include an A2UI JSON 
section at the end of your response. This is OPTIONAL and should only be used when 
the response involves code, questions, or structured feedback.

### Format:
Your normal text response here...

---a2ui_JSON---
[
  {{"type": "component-type", "id": "unique-id", "properties": {{...}}}}
]

### Available Components:
{components_doc}

### Rules:
1. Only include A2UI JSON when it adds value (code display, questions, feedback)
2. Always include a text response BEFORE the JSON
3. Use the ---a2ui_JSON--- delimiter exactly
4. JSON must be a valid array of components
5. Each component needs a unique id

### Example Response:
Here's the fibonacci function you asked about:

---a2ui_JSON---
[
  {{
    "type": "code-editor",
    "id": "fib-code",
    "properties": {{
      "code": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)",
      "language": "python",
      "readonly": true,
      "lineNumbers": true
    }}
  }}
]
"""


def validate_a2ui_response(response: str) -> tuple[bool, str, list[dict[str, Any]] | None]:
    """
    Validate an A2UI response.
    
    Returns:
        tuple: (is_valid, error_message, parsed_json or None)
    """
    if "---a2ui_JSON---" not in response:
        return True, "", None  # No A2UI content, valid plain response
    
    try:
        _, json_part = response.split("---a2ui_JSON---", 1)
        json_str = json_part.strip()
        
        # Clean up markdown code blocks if present
        if json_str.startswith("```"):
            json_str = json_str.lstrip("```json").lstrip("```").rstrip("```").strip()
        
        parsed = json.loads(json_str)
        
        if not isinstance(parsed, list):
            return False, "A2UI JSON must be an array", None
        
        for i, component in enumerate(parsed):
            if "type" not in component:
                return False, f"Component {i} missing 'type' field", None
            if "id" not in component:
                return False, f"Component {i} missing 'id' field", None
        
        return True, "", parsed
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", None
    except ValueError as e:
        return False, f"Parse error: {e}", None


# Export components for use in agents
__all__ = [
    "A2UI_SCHEMA",
    "INTERVIEW_UI_COMPONENTS", 
    "get_a2ui_prompt",
    "validate_a2ui_response"
]
