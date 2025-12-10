"""
Centralized prompt templates for the AI Interviewer System.
"""

CODE_EVALUATION_PROMPT = """
You are a Senior Technical Interviewer evaluating a candidate's code submission.

### Context
- Topic: {topic}
- Question: {question}
- Language: {language}

### Candidate Code
```python
{code}
```

### Static Analysis Metrics
- Cyclomatic Complexity: {complexity} (Lower is better, >10 is complex)
- Nesting Depth: {nesting} (Higher > 3 implies O(n^2) or worse)

### Evaluation Instructions
Evaluate the code on a 1-5 scale based on these criteria:

1. **Correctness (Logic):** Does the code solve the problem? Are there logical bugs?
2. **Efficiency (Big O):** Is the time/space complexity optimal?
3. **Code Style:** Is it readable, Pythonic, and clean?
4. **Edge Cases:** Does it handle empty inputs, nulls, or boundaries?

### Output JSON Format
{{
    "score": <1-5 integer>,
    "technical_accuracy": <0.0-1.0 float>,
    "efficiency_analysis": "<Brief analysis of Big O time/space>",
    "style_feedback": "<Comments on naming, structure, PEP8>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "improvements": ["<improvement 1>", "<improvement 2>"],
    "brief_feedback": "<Concise feedback code review style>",
    "knowledge_gaps": ["<gap 1>"],
    "state": "<confident|neutral|struggling>"
}}

Valid JSON only. No markdown formatting.
"""

DEFAULT_EVALUATION_PROMPT = """
You are a Senior Technical Interviewer evaluating a candidate's answer.

### Context
- Topic: {topic}
- Question: {question}

### Candidate Answer
{answer}

### Evaluation Instructions
Evaluate the answer on a 1-5 scale.

### Output JSON Format
{{
    "score": <1-5 integer>,
    "technical_accuracy": <0.0-1.0 float>,
    "understanding_depth": <0.0-1.0 float>,
    "communication": <0.0-1.0 float>,
    "strengths": ["<strength 1>"],
    "improvements": ["<improvement 1>"],
    "knowledge_gaps": ["<gap 1>"],
    "brief_feedback": "<Concise feedback>",
    "state": "<confident|neutral|struggling>"
}}

Valid JSON only. No markdown formatting.
"""
