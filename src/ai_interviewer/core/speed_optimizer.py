"""
Speed Optimizer - Multi-Tier Caching for Sub-Second Responses
Implements L1/L2/L3 caching strategy for maximum performance
"""

import logging
import time
import sqlite3
import json
import hashlib
import pickle
from typing import Dict, Any, Optional, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    l1_hits: int = 0
    l2_hits: int = 0
    l3_misses: int = 0
    total_requests: int = 0
    avg_l1_time_ms: float = 0.0
    avg_l2_time_ms: float = 0.0
    avg_l3_time_ms: float = 0.0

class L1HotCache:
    """
    L1 Cache: In-memory hot cache for most frequent items
    Target: <10ms access time
    Size: 100 items
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float, int]] = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get from L1 cache"""
        with self.lock:
            if key in self.cache:
                data, timestamp, access_count = self.cache.pop(key)
                # Move to end (most recently used)
                self.cache[key] = (data, timestamp, access_count + 1)
                self.hits += 1
                return data
            
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any):
        """Set in L1 cache with LRU eviction"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)  # Remove oldest
            
            self.cache[key] = (value, time.time(), 1)
    
    def clear(self):
        """Clear L1 cache"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

class L2PersistentCache:
    """
    L2 Cache: SQLite-based persistent cache
    Target: <50ms access time
    Size: 10,000 items
    """
    
    def __init__(self, db_path: str = "./cache/l2_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self.hits = 0
        self.misses = 0
    
    def _init_database(self):
        """Initialize L2 cache database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS l2_cache (
                    cache_key TEXT PRIMARY KEY,
                    cache_value BLOB NOT NULL,
                    cache_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    expiry_time TIMESTAMP
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accessed 
                ON l2_cache(accessed_at DESC)
            """)
            
            # Create index for expiry
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expiry 
                ON l2_cache(expiry_time)
            """)
    
    def get(self, key: str) -> Optional[Any]:
        """Get from L2 cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT cache_value, cache_type, expiry_time 
                    FROM l2_cache 
                    WHERE cache_key = ?
                """, (key,))
                
                row = cursor.fetchone()
                
                if row:
                    value_blob, cache_type, expiry = row
                    
                    # Check expiry
                    if expiry and datetime.fromisoformat(expiry) < datetime.now():
                        # Expired, delete and return None
                        conn.execute("DELETE FROM l2_cache WHERE cache_key = ?", (key,))
                        self.misses += 1
                        return None
                    
                    # Update access stats
                    conn.execute("""
                        UPDATE l2_cache 
                        SET accessed_at = CURRENT_TIMESTAMP,
                            access_count = access_count + 1
                        WHERE cache_key = ?
                    """, (key,))
                    
                    # Deserialize value
                    value = pickle.loads(value_blob)
                    self.hits += 1
                    return value
                
                self.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"L2 cache get error: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, cache_type: str = "general", 
            ttl_hours: Optional[int] = None):
        """Set in L2 cache"""
        try:
            value_blob = pickle.dumps(value)
            
            expiry = None
            if ttl_hours:
                expiry = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO l2_cache 
                    (cache_key, cache_value, cache_type, created_at, accessed_at, 
                     access_count, expiry_time)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?)
                """, (key, value_blob, cache_type, expiry))
                
                # Maintain cache size limit
                conn.execute("""
                    DELETE FROM l2_cache 
                    WHERE cache_key IN (
                        SELECT cache_key FROM l2_cache 
                        ORDER BY accessed_at ASC 
                        LIMIT (SELECT CASE 
                                WHEN COUNT(*) > 10000 
                                THEN COUNT(*) - 10000 
                                ELSE 0 END 
                               FROM l2_cache)
                    )
                """)
                
        except Exception as e:
            logger.error(f"L2 cache set error: {e}")
    
    def clear(self):
        """Clear L2 cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM l2_cache")
        except Exception as e:
            logger.error(f"L2 cache clear error: {e}")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM l2_cache 
                    WHERE expiry_time IS NOT NULL 
                    AND expiry_time < ?
                """, (datetime.now().isoformat(),))
        except Exception as e:
            logger.error(f"L2 cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM l2_cache")
                size = cursor.fetchone()[0]
                
                total = self.hits + self.misses
                hit_rate = self.hits / total if total > 0 else 0.0
                
                return {
                    "size": size,
                    "max_size": 10000,
                    "hits": self.hits,
                    "misses": self.misses,
                    "hit_rate": hit_rate
                }
        except Exception as e:
            logger.error(f"L2 cache stats error: {e}")
            return {"error": str(e)}

class SpeedOptimizer:
    """
    Multi-tier caching system for maximum speed
    
    Architecture:
    L1: Hot cache (in-memory) - <10ms - 100 items
    L2: Persistent cache (SQLite) - <50ms - 10,000 items
    L3: Generation (LLM) - <2s - as needed
    """
    
    def __init__(self):
        self.l1_cache = L1HotCache(max_size=100)
        self.l2_cache = L2PersistentCache()
        
        # Metrics
        self.metrics = CacheMetrics()
        self.metrics_lock = threading.Lock()
        
        # Background cleanup
        self.cleanup_active = True
        self.cleanup_thread = threading.Thread(
            target=self._background_cleanup, 
            daemon=True
        )
        self.cleanup_thread.start()
        
        logger.info("Speed optimizer initialized with multi-tier caching")
    
    def get_or_generate(
        self, 
        key: str, 
        generator: Callable[[], Any],
        cache_type: str = "general",
        ttl_hours: Optional[int] = 24
    ) -> Tuple[Any, float, str]:
        """
        Get from cache or generate with timing
        
        Returns:
            (value, time_ms, cache_level)
        """
        start_time = time.time()
        
        with self.metrics_lock:
            self.metrics.total_requests += 1
        
        # Try L1 (hot cache)
        l1_start = time.time()
        value = self.l1_cache.get(key)
        if value is not None:
            time_ms = (time.time() - l1_start) * 1000
            with self.metrics_lock:
                self.metrics.l1_hits += 1
                self._update_avg_time("l1", time_ms)
            
            logger.debug(f"L1 cache hit: {time_ms:.2f}ms")
            return value, time_ms, "L1"
        
        # Try L2 (persistent cache)
        l2_start = time.time()
        value = self.l2_cache.get(key)
        if value is not None:
            # Promote to L1
            self.l1_cache.set(key, value)
            
            time_ms = (time.time() - l2_start) * 1000
            with self.metrics_lock:
                self.metrics.l2_hits += 1
                self._update_avg_time("l2", time_ms)
            
            logger.debug(f"L2 cache hit (promoted to L1): {time_ms:.2f}ms")
            return value, time_ms, "L2"
        
        # L3: Generate (cache miss)
        l3_start = time.time()
        try:
            value = generator()
            
            # Cache in both L1 and L2
            self.l1_cache.set(key, value)
            self.l2_cache.set(key, value, cache_type, ttl_hours)
            
            time_ms = (time.time() - l3_start) * 1000
            with self.metrics_lock:
                self.metrics.l3_misses += 1
                self._update_avg_time("l3", time_ms)
            
            logger.debug(f"L3 generated and cached: {time_ms:.2f}ms")
            return value, time_ms, "L3"
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            # Return error with timing
            time_ms = (time.time() - l3_start) * 1000
            return None, time_ms, "ERROR"
    
    def _update_avg_time(self, level: str, time_ms: float):
        """Update average time for cache level"""
        if level == "l1":
            n = self.metrics.l1_hits
            avg = self.metrics.avg_l1_time_ms
            self.metrics.avg_l1_time_ms = ((avg * (n - 1)) + time_ms) / n
        elif level == "l2":
            n = self.metrics.l2_hits
            avg = self.metrics.avg_l2_time_ms
            self.metrics.avg_l2_time_ms = ((avg * (n - 1)) + time_ms) / n
        elif level == "l3":
            n = self.metrics.l3_misses
            avg = self.metrics.avg_l3_time_ms
            self.metrics.avg_l3_time_ms = ((avg * (n - 1)) + time_ms) / n
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        with self.metrics_lock:
            total = self.metrics.total_requests
            if total == 0:
                overall_hit_rate = 0.0
            else:
                hits = self.metrics.l1_hits + self.metrics.l2_hits
                overall_hit_rate = hits / total
            
            return {
                "total_requests": total,
                "l1_hits": self.metrics.l1_hits,
                "l2_hits": self.metrics.l2_hits,
                "l3_misses": self.metrics.l3_misses,
                "overall_hit_rate": overall_hit_rate,
                "avg_l1_time_ms": self.metrics.avg_l1_time_ms,
                "avg_l2_time_ms": self.metrics.avg_l2_time_ms,
                "avg_l3_time_ms": self.metrics.avg_l3_time_ms,
                "l1_stats": self.l1_cache.get_stats(),
                "l2_stats": self.l2_cache.get_stats()
            }
    
    def clear_all_caches(self):
        """Clear all cache levels"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        logger.info("All caches cleared")
    
    def _background_cleanup(self):
        """Background cleanup task"""
        while self.cleanup_active:
            try:
                time.sleep(3600)  # Every hour
                
                # Cleanup expired L2 entries
                self.l2_cache.cleanup_expired()
                
                logger.info("Background cache cleanup completed")
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
    
    def shutdown(self):
        """Shutdown optimizer"""
        self.cleanup_active = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        logger.info("Speed optimizer shutdown complete")


# Decorator for automatic caching
def speed_cached(cache_type: str = "general", ttl_hours: int = 24):
    """
    Decorator to automatically cache function results
    
    Usage:
        @speed_cached(cache_type="questions", ttl_hours=48)
        def generate_question(topic, difficulty):
            # Expensive generation
            return question
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Get global speed optimizer
            optimizer = _get_global_optimizer()
            
            # Generate cache key
            cache_key = optimizer.cache_key(
                func.__name__, 
                *args, 
                **kwargs
            )
            
            # Get or generate with caching
            result, time_ms, level = optimizer.get_or_generate(
                key=cache_key,
                generator=lambda: func(*args, **kwargs),
                cache_type=cache_type,
                ttl_hours=ttl_hours
            )
            
            return result
        
        return wrapper
    return decorator


# Global optimizer instance
_global_optimizer = None

def _get_global_optimizer() -> SpeedOptimizer:
    """Get global speed optimizer instance"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = SpeedOptimizer()
    return _global_optimizer

def get_speed_optimizer() -> SpeedOptimizer:
    """Public API to get speed optimizer"""
    return _get_global_optimizer()
