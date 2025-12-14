# 🔍 Type Checking Troubleshooting Guide

> **Last Updated:** 2025-12-14  
> **Purpose:** Comprehensive guide for resolving mypy type checking errors, especially when CI fails but local passes

---

## 📋 Table of Contents

1. [Common Issues & Solutions](#common-issues--solutions)
2. [Local vs CI Environment Differences](#local-vs-ci-environment-differences)
3. [Type Error Patterns & Fixes](#type-error-patterns--fixes)
4. [Best Practices](#best-practices)
5. [Quick Reference](#quick-reference)

---

## Common Issues & Solutions

### Issue 1: CI Fails but Local Passes

**Symptoms:**
- `mypy` passes locally: `Success: no issues found in 37 source files`
- CI shows errors: `error: Unused "type: ignore" comment [unused-ignore]`

**Root Causes:**
1. **Different mypy versions** - CI uses latest from pip, local may have cached version
2. **Type cache differences** - Local may have cached type information
3. **Stricter enforcement** - CI enforces `warn_unused_ignores = True` more strictly
4. **Environment differences** - Python version, dependency versions differ

**Solution:**
- Always test with fresh environment: `pip install --upgrade mypy`
- Clear mypy cache: `rm -rf .mypy_cache`
- Use explicit type handling instead of `type: ignore` when possible

---

### Issue 2: Unused Type Ignore Comments

**Error:**
```
error: Unused "type: ignore" comment [unused-ignore]
```

**Cause:**
- `warn_unused_ignores = True` in `mypy.ini` flags unnecessary suppressions
- The code doesn't actually need the ignore comment

**Fix:**
```python
# ❌ BAD: Unused ignore
return interface  # type: ignore[no-any-return]

# ✅ GOOD: Use explicit cast
from typing import cast
return cast(gr.Blocks, interface)
```

**Why This Works:**
- `cast()` explicitly tells mypy the expected type
- More type-safe than suppressing errors
- Works consistently across environments

---

### Issue 3: Incompatible Type Assignments

**Error:**
```
error: Incompatible types in assignment (expression has type "None", variable has type "Callable[...]") [assignment]
```

**Example:**
```python
# ❌ BAD: Assigning None to a Callable type
try:
    from docx import Document
except ImportError:
    Document = None  # Error: Can't assign None to Callable
```

**Fix:**
```python
# ✅ GOOD: Use a flag instead
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    # Don't assign None to Document

# Later in code:
if not DOCX_AVAILABLE:
    return None
from docx import Document  # Re-import when needed
doc = Document(file_obj)
```

**Why This Works:**
- Avoids type incompatibility entirely
- Uses flag for availability checks
- Re-imports when actually needed

---

### Issue 4: Missing Return Type Annotations

**Error:**
```
error: Function is missing a return type annotation [no-any-return]
```

**Fix:**
```python
# ❌ BAD: Missing return type
def process_answer(self, text: str) -> Any:
    return {"status": "ok"}

# ✅ GOOD: Explicit return type
def process_answer(self, text: str) -> Dict[str, Any]:
    return {"status": "ok"}

# ✅ BETTER: Use TypedDict
class AnswerResponse(TypedDict):
    status: str
    score: float
    feedback: str

def process_answer(self, text: str) -> AnswerResponse:
    return {"status": "ok", "score": 8.5, "feedback": "Good"}
```

---

### Issue 5: Optional Type Issues

**Error:**
```
error: Incompatible default for argument "x" (default has type "None", argument has type "str") [assignment]
```

**Fix:**
```python
# ❌ BAD: Implicit Optional
def func(x: str = None):  # Error: None not compatible with str
    pass

# ✅ GOOD: Explicit Optional
def func(x: Optional[str] = None):
    pass
```

**Configuration:**
- `no_implicit_optional = True` in `mypy.ini` requires explicit `Optional[]`

---

### Issue 6: Union Type Mismatches

**Error:**
```
error: Incompatible types in assignment (expression has type "X", variable has type "Y") [assignment]
```

**Fix:**
```python
# ❌ BAD: Type mismatch
self.flow_controller: InterviewGraph = AutonomousFlowController()

# ✅ GOOD: Use Union type
from typing import Union
self.flow_controller: Union[InterviewGraph, AutonomousFlowController] = AutonomousFlowController()
```

---

## Local vs CI Environment Differences

| Aspect | Local Environment | CI Environment | Impact |
|--------|------------------|----------------|--------|
| **Python Version** | 3.11.9 (varies) | 3.10 (configured) | Type checking may differ |
| **Mypy Version** | 1.19.0 (may be cached) | Latest from pip | Newer versions stricter |
| **Type Cache** | May have `.mypy_cache/` | Fresh every run | Cached types may hide errors |
| **Strictness** | May be more lenient | Strict enforcement | CI catches more issues |
| **Unused Ignores** | May not flag | Flags with `warn_unused_ignores = True` | CI requires clean code |
| **Dependencies** | May have different versions | Exact versions from `requirements.txt` | Type stubs may differ |

### How to Match CI Environment Locally

```bash
# 1. Use same Python version
python --version  # Should be 3.10

# 2. Upgrade mypy to latest
pip install --upgrade mypy

# 3. Clear type cache
rm -rf .mypy_cache

# 4. Run with same config
mypy src/ --config-file mypy.ini

# 5. Check for unused ignores
mypy src/ --config-file mypy.ini --warn-unused-ignores
```

---

## Type Error Patterns & Fixes

### Pattern 1: Optional Imports

**Problem:**
```python
try:
    from optional_module import Class
except ImportError:
    Class = None  # Type error
```

**Solution:**
```python
try:
    from optional_module import Class
    MODULE_AVAILABLE = True
except ImportError:
    MODULE_AVAILABLE = False
    # Don't assign None

# Usage:
if not MODULE_AVAILABLE:
    return None
from optional_module import Class  # Re-import when needed
```

---

### Pattern 2: LLM Return Types

**Problem:**
```python
def get_response(self) -> Dict[str, Any]:
    result = llm.invoke(prompt)  # Returns Any
    return result  # Error: Returning Any
```

**Solution:**
```python
from typing import cast

def get_response(self) -> Dict[str, Any]:
    result = llm.invoke(prompt)
    return cast(Dict[str, Any], result)  # Explicit cast
```

---

### Pattern 3: SecretStr for API Keys

**Problem:**
```python
api_key = os.environ.get("API_KEY")  # str | None
llm = ChatOpenAI(api_key=api_key)  # Error: Expected SecretStr
```

**Solution:**
```python
from pydantic import SecretStr

api_key = os.environ.get("API_KEY")
if api_key:
    if PYDANTIC_AVAILABLE and SecretStr is not None:
        api_key_secret: Any = SecretStr(api_key)
    else:
        api_key_secret = api_key
    llm = ChatOpenAI(api_key=api_key_secret)
```

---

### Pattern 4: TypedDict vs Dict[str, Any]

**Problem:**
```python
def get_response() -> Dict[str, Any]:  # Too generic
    return {"status": "ok", "data": {...}}
```

**Solution:**
```python
from typing import TypedDict

class Response(TypedDict):
    status: str
    data: Dict[str, Any]

def get_response() -> Response:
    return {"status": "ok", "data": {...}}
```

---

### Pattern 5: Protocol vs Implementation Mismatch

**Problem:**
```python
# Protocol says:
def process_answer(self, text: str) -> Tuple[Any, ...]:

# Implementation returns:
def process_answer(self, text: str) -> Dict[str, Any]:
    return {"status": "ok"}  # Mismatch!
```

**Solution:**
```python
# Update protocol to match implementation
def process_answer(self, text: str) -> Dict[str, Any]:
    ...
```

---

## Best Practices

### 1. Prefer `cast()` Over `type: ignore`

```python
# ❌ Avoid when possible
result = some_function()  # type: ignore[no-any-return]

# ✅ Better
from typing import cast
result = cast(ExpectedType, some_function())
```

**Why:**
- More explicit and type-safe
- Works consistently across environments
- Avoids "unused ignore" warnings

---

### 2. Use TypedDict for Structured Data

```python
# ❌ Avoid
def get_data() -> Dict[str, Any]:
    return {"name": "John", "age": 30}

# ✅ Better
class PersonData(TypedDict):
    name: str
    age: int

def get_data() -> PersonData:
    return {"name": "John", "age": 30}
```

---

### 3. Avoid Assigning None to Typed Variables

```python
# ❌ Avoid
try:
    from module import Class
except ImportError:
    Class = None  # Type error

# ✅ Better
try:
    from module import Class
    CLASS_AVAILABLE = True
except ImportError:
    CLASS_AVAILABLE = False
```

---

### 4. Use Explicit Optional Types

```python
# ❌ Avoid (with no_implicit_optional = True)
def func(x: str = None):
    pass

# ✅ Better
def func(x: Optional[str] = None):
    pass
```

---

### 5. Test in Clean Environment

```bash
# Before committing, test in clean environment
pip install --upgrade mypy
rm -rf .mypy_cache
mypy src/ --config-file mypy.ini
```

---

## Quick Reference

### Common Mypy Error Codes

| Error Code | Meaning | Common Fix |
|------------|---------|------------|
| `unused-ignore` | Type ignore not needed | Remove or use `cast()` |
| `assignment` | Type mismatch in assignment | Use Union type or cast |
| `no-any-return` | Returning Any from typed function | Add explicit return type or cast |
| `arg-type` | Wrong argument type | Fix argument type or cast |
| `return-value` | Wrong return type | Fix return type or cast |
| `name-defined` | Name not defined | Check imports and scope |
| `unreachable` | Unreachable code | Remove or restructure |

### Mypy Configuration Flags

| Flag | Purpose | Value in Project |
|------|---------|------------------|
| `warn_unused_ignores` | Flag unused type ignores | `True` |
| `no_implicit_optional` | Require explicit Optional | `True` |
| `warn_return_any` | Warn on Any returns | `True` |
| `warn_unreachable` | Detect unreachable code | `True` |
| `ignore_missing_imports` | Ignore missing type stubs | `True` (for optional deps) |

### Type Checking Commands

```bash
# Basic check
mypy src/ --config-file mypy.ini

# Check specific file
mypy src/ui/app.py --config-file mypy.ini

# Show error codes
mypy src/ --config-file mypy.ini --show-error-codes

# Check for unused ignores
mypy src/ --config-file mypy.ini --warn-unused-ignores

# Clear cache and check
rm -rf .mypy_cache && mypy src/ --config-file mypy.ini
```

---

## Real-World Examples from This Project

### Example 1: UI Return Type

**File:** `src/ui/app.py`

**Problem:**
```python
return interface  # type: ignore[no-any-return]
# CI Error: Unused "type: ignore" comment
```

**Solution:**
```python
from typing import cast
return cast(gr.Blocks, interface)
```

---

### Example 2: Optional Document Import

**File:** `src/ai_interviewer/core/resume_parser.py`

**Problem:**
```python
try:
    from docx import Document
except ImportError:
    Document = None  # Error: Incompatible types
```

**Solution:**
```python
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    # Don't assign None

# Usage:
if not DOCX_AVAILABLE:
    return None
from docx import Document  # Re-import
doc = Document(file_obj)
```

---

### Example 3: Union Type for Flow Controller

**File:** `src/ai_interviewer/controller.py`

**Problem:**
```python
self.flow_controller: InterviewGraph = AutonomousFlowController()
# Error: Incompatible types
```

**Solution:**
```python
from typing import Union
self.flow_controller: Union[InterviewGraph, AutonomousFlowController] = AutonomousFlowController()
```

---

### Example 4: SecretStr for API Keys

**File:** `src/ai_interviewer/core/autonomous_reasoning_engine.py`

**Problem:**
```python
api_key = os.environ.get("OPENAI_API_KEY")  # str | None
llm = ChatOpenAI(api_key=api_key)  # Error: Expected SecretStr
```

**Solution:**
```python
from pydantic import SecretStr

api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    if PYDANTIC_AVAILABLE and SecretStr is not None:
        api_key_secret: Any = SecretStr(api_key)
    else:
        api_key_secret = api_key
    llm = ChatOpenAI(api_key=api_key_secret)
```

---

## Troubleshooting Checklist

When CI fails but local passes:

- [ ] Check mypy version: `mypy --version`
- [ ] Clear type cache: `rm -rf .mypy_cache`
- [ ] Upgrade mypy: `pip install --upgrade mypy`
- [ ] Run with same config: `mypy src/ --config-file mypy.ini`
- [ ] Check for unused ignores: `--warn-unused-ignores`
- [ ] Verify Python version matches CI (3.10)
- [ ] Check if dependencies differ
- [ ] Review error messages carefully
- [ ] Replace `type: ignore` with `cast()` when possible
- [ ] Avoid assigning `None` to typed variables

---

## Additional Resources

- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [TypedDict Documentation](https://www.python.org/dev/peps/pep-0589/)
- [Project Type Checking Setup](docs/SETUP.md#type-checking-development)

---

**Last Updated:** 2025-12-14  
**Maintained By:** Development Team  
**Related Docs:** [CONTRIBUTING.md](CONTRIBUTING.md), [SETUP.md](SETUP.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

