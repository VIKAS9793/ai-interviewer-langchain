"""Mock LLM for testing rate limiter without consuming API quota."""

class AIMessage:
    """Mock AIMessage to simulate LangChain response format."""
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self):
        return self.content


class MockGemini:
    """
    Simulates Gemini API with 20 RPD quota limit.
    Raises 429 error after quota exhausted.
    """
    
    def __init__(self, quota_limit: int = 20):
        self.call_count = 0
        self.quota_limit = quota_limit
        self.name = "MockGemini"
    
    def invoke(self, prompt: str) -> AIMessage:
        """Simulate Gemini invoke with quota tracking."""
        self.call_count += 1
        
        if self.call_count > self.quota_limit:
            raise Exception("429 ResourceExhausted: quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests")
        
        return AIMessage(content=f"Mock Gemini response #{self.call_count}")
    
    def reset(self):
        """Reset call counter for testing."""
        self.call_count = 0


class MockHuggingFace:
    """
    Unlimited mock fallback LLM.
    Simulates HuggingFace API without quota limits.
    """
    
    def __init__(self):
        self.call_count = 0
        self.name = "MockHuggingFace"
    
    def invoke(self, prompt: str) -> AIMessage:
        """Simulate HuggingFace invoke (unlimited)."""
        self.call_count += 1
        return AIMessage(content=f"Mock HuggingFace response #{self.call_count}")
    
    def reset(self):
        """Reset call counter for testing."""
        self.call_count = 0
