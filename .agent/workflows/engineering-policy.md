---
description: Engineering standards and code quality rules for this project
---

# AI Interviewer - Engineering Policy

**Load this at the start of any coding session.**

## NON-NEGOTIABLES (Zero Tolerance)

1. **NO print()** - Use `logger.warning()` or `logger.error()`
2. **NO bare except:** - Catch specific exceptions
3. **NO unpinned deps** - Pin all in requirements.txt
4. **NO hardcoded secrets** - Use `os.getenv()`
5. **NO TODO in commits** - Resolve or remove

## Required Patterns

```python
# Logging
import logging
logger = logging.getLogger(__name__)

# Error handling
try:
    risky()
except SpecificError as e:
    logger.error(f"Known error: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    raise

# Type hints
def process(data: str) -> dict:
    ...

# Docstrings
def evaluate(answer: str) -> dict:
    """Evaluate candidate answer.
    
    Args:
        answer: Response text
    Returns:
        dict with score and feedback
    """
```

## Pre-Commit Checklist

- [ ] No print() statements
- [ ] Dependencies pinned
- [ ] Type hints on new functions
- [ ] Docstrings on public functions
- [ ] Import test passes

## Architecture

- 6 sub-agents (interviewer, resume, coding, safety, study, critic)
- Factory pattern: `create_*_agent()`
- Config via environment variables
- File upload via ADK artifacts

## Commands

```bash
# Run
adk web src/adk_interviewer

# Test imports
python -c "from src.adk_interviewer.agent import root_agent"

# Check for print statements
grep -r "print(" src/ --include="*.py" | grep -v ">>>"
```
