"""
API Rate Limiter for AI Interviewer.

Enterprise-grade rate limiting following MAANG best practices:
- Token Bucket algorithm for burst-friendly limiting
- Exponential backoff with jitter for retry logic
- Daily quota tracking to stay within free tier
- Thread-safe implementation

References:
- Google Cloud Gemini API Rate Limiting Docs
- AWS Architecture Best Practices
- Enterprise API Gateway Patterns (Kong, Envoy)
"""

import time
import random
import threading
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, TypeVar, Any
from functools import wraps
from datetime import datetime, timezone

from ..utils.config import Config
from ..exceptions import ResourceError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Requests per minute (RPM)
    requests_per_minute: int = 15  # Default: conservative limit
    # Requests per day (RPD)
    requests_per_day: int = 1000  # Conservative for 5 users × 20 calls
    # Tokens per minute (TPM) - for future use
    tokens_per_minute: int = 250000
    
    # Retry configuration
    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.5  # ±50% random jitter


@dataclass
class TokenBucket:
    """
    Thread-safe Token Bucket implementation.
    
    Allows bursts up to bucket capacity while maintaining average rate.
    Preferred over Leaky Bucket for AI Interviewer's sporadic traffic pattern.
    """
    capacity: int
    refill_rate: float  # Tokens per second
    _tokens: float = field(init=False)
    _last_refill: float = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    
    def __post_init__(self) -> None:
        self._tokens = float(self.capacity)
        self._last_refill = time.time()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        tokens_to_add = elapsed * self.refill_rate
        self._tokens = min(self.capacity, self._tokens + tokens_to_add)
        self._last_refill = now
    
    def acquire(self, tokens: int = 1, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            blocking: If True, wait for tokens. If False, return immediately
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if tokens acquired, False otherwise
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill()
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                
                if not blocking:
                    return False
                
                # Calculate wait time for tokens to be available
                tokens_needed = tokens - self._tokens
                wait_time = tokens_needed / self.refill_rate
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait_time > timeout:
                    return False
            
            # Wait for tokens (with small buffer for refill timing)
            time.sleep(min(wait_time + 0.1, 1.0))
    
    @property
    def available_tokens(self) -> float:
        """Get current available tokens."""
        with self._lock:
            self._refill()
            return self._tokens


@dataclass
class DailyQuotaTracker:
    """
    Track daily API usage to stay within free tier limits.
    
    Resets at midnight Pacific Time (per Google's quota reset).
    """
    daily_limit: int
    _count: int = field(default=0, init=False)
    _reset_date: str = field(default="", init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    
    def __post_init__(self) -> None:
        self._reset_date = self._get_current_date()
    
    @staticmethod
    def _get_current_date() -> str:
        """Get current date in Pacific Time (Google's reset time)."""
        # Simplified: use UTC date for now
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _check_reset(self) -> None:
        """Reset counter if it's a new day."""
        current_date = self._get_current_date()
        if current_date != self._reset_date:
            logger.info(f"🔄 Daily quota reset: {self._reset_date} -> {current_date}")
            self._count = 0
            self._reset_date = current_date
    
    def can_make_request(self) -> bool:
        """Check if we're within daily quota."""
        with self._lock:
            self._check_reset()
            return self._count < self.daily_limit
    
    def record_request(self) -> None:
        """Record an API request."""
        with self._lock:
            self._check_reset()
            self._count += 1
            
            # Warn at 80% usage
            usage_pct = (self._count / self.daily_limit) * 100
            if usage_pct >= 80 and (self._count - 1) / self.daily_limit * 100 < 80:
                logger.warning(f"⚠️ Daily quota at {usage_pct:.0f}%: {self._count}/{self.daily_limit}")
    
    @property
    def remaining(self) -> int:
        """Get remaining daily requests."""
        with self._lock:
            self._check_reset()
            return max(0, self.daily_limit - self._count)
    
    @property
    def usage_stats(self) -> dict:
        """Get usage statistics."""
        with self._lock:
            self._check_reset()
            return {
                "used": self._count,
                "limit": self.daily_limit,
                "remaining": max(0, self.daily_limit - self._count),
                "usage_pct": round((self._count / self.daily_limit) * 100, 1),
                "reset_date": self._reset_date
            }


class GlobalInterviewQuota:
    """
    Track global interview completions per day.
    
    Enforces hard limit: 1 interview per day for entire system.
    After ANY user completes an interview, block all subsequent users.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._interviews_completed = 0
        self._reset_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("🔒 GlobalInterviewQuota initialized: 1 interview/day limit")
    
    def _check_reset(self) -> None:
        """Reset counter if it's a new day."""
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if current_date != self._reset_date:
            logger.info(f"🔄 Global interview quota reset: {self._reset_date} -> {current_date}")
            self._interviews_completed = 0
            self._reset_date = current_date
    
    def can_start_interview(self) -> bool:
        """Check if a new interview can be started today."""
        with self._lock:
            self._check_reset()
            return self._interviews_completed < 1
    
    def record_interview_completion(self) -> None:
        """Record that an interview was completed."""
        with self._lock:
            self._check_reset()
            self._interviews_completed += 1
            logger.warning(f"⚠️ Daily interview quota exhausted: {self._interviews_completed}/1")
    
    @property
    def is_quota_exhausted(self) -> bool:
        """Check if daily quota is exhausted."""
        with self._lock:
            self._check_reset()
            return self._interviews_completed >= 1
    
    @property
    def stats(self) -> dict:
        """Get global quota statistics."""
        with self._lock:
            self._check_reset()
            return {
                "interviews_completed": self._interviews_completed,
                "daily_limit": 1,
                "quota_exhausted": self._interviews_completed >= 1,
                "reset_date": self._reset_date
            }


# Global singleton
def get_global_interview_quota() -> GlobalInterviewQuota:
    """Get the global interview quota tracker."""
    return GlobalInterviewQuota()


class APIRateLimiter:
    """
    Enterprise-grade API rate limiter for LLM calls.
    
    Features:
    - Token bucket for RPM limiting (burst-friendly)
    - Daily quota tracking for RPD limits
    - Exponential backoff with jitter for retries
    - Thread-safe implementation
    
    Usage:
        limiter = APIRateLimiter()
        
        @limiter.rate_limited
        def call_llm(prompt: str) -> str:
            return llm.invoke(prompt)
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        
        # Token bucket for RPM
        self.rpm_bucket = TokenBucket(
            capacity=self.config.requests_per_minute,
            refill_rate=self.config.requests_per_minute / 60.0
        )
        
        # Daily quota tracker for RPD
        self.daily_quota = DailyQuotaTracker(
            daily_limit=self.config.requests_per_day
        )
        
        logger.info(
            f"🔧 Rate limiter initialized: "
            f"{self.config.requests_per_minute} RPM, "
            f"{self.config.requests_per_day} RPD"
        )
    
    def wait_for_capacity(self, timeout: Optional[float] = 30.0) -> bool:
        """
        Wait for rate limit capacity.
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if capacity available, False if timeout or quota exhausted
        """
        # Check daily quota first
        if not self.daily_quota.can_make_request():
            logger.error("❌ Daily quota exhausted")
            raise ResourceError(
                "Daily API quota exhausted. Please try again tomorrow.",
                resource_type="api_quota",
                limit=self.config.requests_per_day
            )
        
        # Wait for RPM capacity
        if self.rpm_bucket.acquire(blocking=True, timeout=timeout):
            self.daily_quota.record_request()
            return True
        
        logger.warning("⚠️ Rate limit timeout - no capacity available")
        return False
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Formula: delay = min(initial * (multiplier ^ attempt) ± jitter, max_delay)
        
        Args:
            attempt: Current retry attempt (0-indexed)
            
        Returns:
            Delay in seconds
        """
        base_delay = self.config.initial_delay_seconds * (
            self.config.backoff_multiplier ** attempt
        )
        
        # Add jitter to prevent thundering herd
        jitter = base_delay * self.config.jitter_factor * (random.random() * 2 - 1)
        delay = base_delay + jitter
        
        return min(max(0.1, delay), self.config.max_delay_seconds)
    
    def rate_limited(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to apply rate limiting with automatic retry.
        
        Handles 429 (rate limit) and 503 (service unavailable) errors
        with exponential backoff.
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_error: Optional[Exception] = None
            
            for attempt in range(self.config.max_retries + 1):
                try:
                    # Wait for capacity
                    self.wait_for_capacity()
                    
                    # Execute function
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    error_str = str(e).lower()
                    
                    # Check if retryable error
                    is_rate_limit = any(x in error_str for x in [
                        "429", "rate", "limit", "quota", "resource_exhausted"
                    ])
                    is_server_error = any(x in error_str for x in [
                        "500", "502", "503", "504", "unavailable", "timeout"
                    ])
                    
                    if not (is_rate_limit or is_server_error):
                        # Non-retryable error, raise immediately
                        raise
                    
                    last_error = e
                    
                    if attempt < self.config.max_retries:
                        delay = self.calculate_backoff(attempt)
                        logger.warning(
                            f"⏳ Retry {attempt + 1}/{self.config.max_retries} "
                            f"after {delay:.1f}s: {type(e).__name__}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"❌ Max retries exceeded: {type(e).__name__}: {e}"
                        )
            
            # All retries exhausted
            if last_error:
                raise last_error
            raise RuntimeError("Rate limiter failed unexpectedly")
        
        return wrapper
    
    @property
    def stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            "rpm": {
                "available": round(self.rpm_bucket.available_tokens, 1),
                "capacity": self.config.requests_per_minute
            },
            "daily": self.daily_quota.usage_stats,
            "config": {
                "max_retries": self.config.max_retries,
                "initial_delay": self.config.initial_delay_seconds,
                "max_delay": self.config.max_delay_seconds
            }
        }


# Singleton instance for global rate limiting
_rate_limiter: Optional[APIRateLimiter] = None
_limiter_lock = threading.Lock()


def get_rate_limiter() -> APIRateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    
    with _limiter_lock:
        if _rate_limiter is None:
            _rate_limiter = APIRateLimiter(RateLimitConfig(
                requests_per_minute=10,     # gemini-2.5-flash-lite
                requests_per_day=20,        # gemini-2.5-flash-lite: 1 interview/day
                max_retries=3,
                initial_delay_seconds=1.0,
                max_delay_seconds=60.0
            ))
        return _rate_limiter
