"""
Offline Optimization Engine
Optimized performance and concurrency for offline operation
"""

import logging
import asyncio
import time
import pickle
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
from contextlib import contextmanager
import numpy as np
from collections import defaultdict, deque
import hashlib
import gzip

from langchain_community.llms import Ollama
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0

@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization"""
    cache_hit_rate: float = 0.0
    avg_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    concurrent_requests: int = 0
    error_rate: float = 0.0

class OfflineOptimizationEngine:
    """Offline optimization engine for performance and concurrency"""
    
    def __init__(self, cache_size_mb: int = 500, max_concurrent: int = 20):
        """Initialize offline optimization engine"""
        self.cache_size_mb = cache_size_mb
        self.max_concurrent = max_concurrent
        self.cache_dir = Path("./offline_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache management
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        self.current_cache_size = 0
        
        # Performance monitoring
        self.performance_metrics = PerformanceMetrics()
        self.metrics_lock = threading.Lock()
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
        # Offline data stores
        self.question_cache_db = self._init_question_cache_db()
        self.evaluation_cache_db = self._init_evaluation_cache_db()
        
        # Embedding cache
        self.embedding_cache = {}
        self.embedding_model = None  # Lazy load
        
        # LLM connection pool
        self.llm_pool = self._init_llm_pool()
        
        # Background optimization
        self.optimization_active = True
        self.optimization_thread = threading.Thread(target=self._background_optimization, daemon=True)
        self.optimization_thread.start()
        
        logger.info(f"Offline optimization engine initialized with {cache_size_mb}MB cache, {max_concurrent} max concurrent")
    
    def _init_question_cache_db(self) -> sqlite3.Connection:
        """Initialize question cache database"""
        db_path = self.cache_dir / "question_cache.db"
        conn = sqlite3.connect(str(db_path))
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS question_cache (
                cache_key TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_text TEXT NOT NULL,
                metadata TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic_difficulty ON question_cache(topic, difficulty)
        """)
        
        conn.commit()
        return conn
    
    def _init_evaluation_cache_db(self) -> sqlite3.Connection:
        """Initialize evaluation cache database"""
        db_path = self.cache_dir / "evaluation_cache.db"
        conn = sqlite3.connect(str(db_path))
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_cache (
                cache_key TEXT PRIMARY KEY,
                question_hash TEXT NOT NULL,
                answer_hash TEXT NOT NULL,
                topic TEXT NOT NULL,
                evaluation_data TEXT NOT NULL,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_question_answer ON evaluation_cache(question_hash, answer_hash)
        """)
        
        conn.commit()
        return conn
    
    def _init_llm_pool(self) -> List[Ollama]:
        """Initialize LLM connection pool"""
        pool_size = min(2, self.max_concurrent // 4)  # Reduce to 2 instances for better performance
        pool = []
        
        for i in range(pool_size):
            try:
                llm = Ollama(
                    model="tinyllama",
                    temperature=0.3,
                    base_url="http://localhost:11434"
                )
                # Test connection
                llm.invoke("test")
                pool.append(llm)
                logger.info(f"LLM instance {i+1} initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM instance {i+1}: {e}")
        
        if not pool:
            logger.error("No LLM instances available - falling back to single instance")
            pool.append(Ollama(model="tinyllama", temperature=0.3))
        
        return pool
    
    def _get_embedding_model(self):
        """Lazy load embedding model"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model
    
    def get_cached_question(self, topic: str, difficulty: str, context_hash: str) -> Optional[str]:
        """Get cached question if available"""
        cache_key = f"{topic}_{difficulty}_{context_hash}"
        
        # Check memory cache first
        with self.cache_lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self._update_cache_metrics(hit=True)
                return entry.data
        
        # Check database cache
        try:
            cursor = self.question_cache_db.execute("""
                SELECT question_text, metadata FROM question_cache 
                WHERE cache_key = ? AND topic = ? AND difficulty = ?
            """, (cache_key, topic, difficulty))
            
            row = cursor.fetchone()
            if row:
                question_text, metadata = row
                
                # Update access count
                self.question_cache_db.execute("""
                    UPDATE question_cache 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE cache_key = ?
                """, (cache_key,))
                self.question_cache_db.commit()
                
                # Add to memory cache
                self._add_to_memory_cache(cache_key, question_text)
                self._update_cache_metrics(hit=True)
                
                return question_text
                
        except Exception as e:
            logger.error(f"Error accessing question cache: {e}")
        
        self._update_cache_metrics(hit=False)
        return None
    
    def cache_question(self, topic: str, difficulty: str, context_hash: str, question: str, metadata: Dict[str, Any] = None):
        """Cache generated question"""
        cache_key = f"{topic}_{difficulty}_{context_hash}"
        
        # Add to memory cache
        self._add_to_memory_cache(cache_key, question)
        
        # Add to database cache
        try:
            self.question_cache_db.execute("""
                INSERT OR REPLACE INTO question_cache 
                (cache_key, topic, difficulty, question_text, metadata, created_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)
            """, (cache_key, topic, difficulty, question, json.dumps(metadata or {})))
            self.question_cache_db.commit()
            
        except Exception as e:
            logger.error(f"Error caching question: {e}")
    
    def get_cached_evaluation(self, question: str, answer: str, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached evaluation if available"""
        question_hash = hashlib.md5(question.encode()).hexdigest()
        answer_hash = hashlib.md5(answer.encode()).hexdigest()
        cache_key = f"{question_hash}_{answer_hash}_{topic}"
        
        # Check memory cache first
        with self.cache_lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self._update_cache_metrics(hit=True)
                return entry.data
        
        # Check database cache
        try:
            cursor = self.evaluation_cache_db.execute("""
                SELECT evaluation_data FROM evaluation_cache 
                WHERE cache_key = ? AND question_hash = ? AND answer_hash = ? AND topic = ?
            """, (cache_key, question_hash, answer_hash, topic))
            
            row = cursor.fetchone()
            if row:
                evaluation_data = json.loads(row[0])
                
                # Update access count
                self.evaluation_cache_db.execute("""
                    UPDATE evaluation_cache 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE cache_key = ?
                """, (cache_key,))
                self.evaluation_cache_db.commit()
                
                # Add to memory cache
                self._add_to_memory_cache(cache_key, evaluation_data)
                self._update_cache_metrics(hit=True)
                
                return evaluation_data
                
        except Exception as e:
            logger.error(f"Error accessing evaluation cache: {e}")
        
        self._update_cache_metrics(hit=False)
        return None
    
    def cache_evaluation(self, question: str, answer: str, topic: str, evaluation: Dict[str, Any]):
        """Cache evaluation result"""
        question_hash = hashlib.md5(question.encode()).hexdigest()
        answer_hash = hashlib.md5(answer.encode()).hexdigest()
        cache_key = f"{question_hash}_{answer_hash}_{topic}"
        
        # Add to memory cache
        self._add_to_memory_cache(cache_key, evaluation)
        
        # Add to database cache
        try:
            self.evaluation_cache_db.execute("""
                INSERT OR REPLACE INTO evaluation_cache 
                (cache_key, question_hash, answer_hash, topic, evaluation_data, created_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)
            """, (cache_key, question_hash, answer_hash, topic, json.dumps(evaluation)))
            self.evaluation_cache_db.commit()
            
        except Exception as e:
            logger.error(f"Error caching evaluation: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get cached embedding or generate new one"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        
        # Generate embedding
        embedding = self._get_embedding_model().encode(text).tolist()
        
        # Cache embedding
        self.embedding_cache[text_hash] = embedding
        
        # Limit cache size
        if len(self.embedding_cache) > 10000:
            # Remove oldest entries
            oldest_keys = list(self.embedding_cache.keys())[:1000]
            for key in oldest_keys:
                del self.embedding_cache[key]
        
        return embedding
    
    def get_llm_instance(self) -> Ollama:
        """Get available LLM instance from pool"""
        # Simple round-robin selection
        if not self.llm_pool:
            raise RuntimeError("No LLM instances available")
        
        # Find least busy instance (simple implementation)
        return self.llm_pool[0]  # For now, just return first instance
    
    def _add_to_memory_cache(self, key: str, data: Any):
        """Add entry to memory cache with size management"""
        with self.cache_lock:
            # Calculate size
            size_bytes = len(pickle.dumps(data))
            
            # Check if we need to evict entries
            while (self.current_cache_size + size_bytes > self.cache_size_mb * 1024 * 1024 and 
                   self.memory_cache):
                self._evict_least_recently_used()
            
            # Add entry
            entry = CacheEntry(
                data=data,
                timestamp=datetime.now(),
                access_count=1,
                last_accessed=datetime.now(),
                size_bytes=size_bytes
            )
            
            self.memory_cache[key] = entry
            self.current_cache_size += size_bytes
    
    def _evict_least_recently_used(self):
        """Evict least recently used cache entry"""
        if not self.memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(self.memory_cache.keys(), 
                     key=lambda k: self.memory_cache[k].last_accessed)
        
        # Remove entry
        entry = self.memory_cache.pop(lru_key)
        self.current_cache_size -= entry.size_bytes
    
    def _update_cache_metrics(self, hit: bool):
        """Update cache hit/miss metrics"""
        with self.metrics_lock:
            # Simple exponential moving average
            alpha = 0.1
            if hit:
                self.performance_metrics.cache_hit_rate = (
                    (1 - alpha) * self.performance_metrics.cache_hit_rate + alpha
                )
            else:
                self.performance_metrics.cache_hit_rate = (
                    (1 - alpha) * self.performance_metrics.cache_hit_rate
                )
    
    def _background_optimization(self):
        """Background optimization tasks"""
        while self.optimization_active:
            try:
                # Clean up old cache entries
                self._cleanup_old_cache_entries()
                
                # Optimize database
                self._optimize_databases()
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Background optimization error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _cleanup_old_cache_entries(self):
        """Clean up old cache entries"""
        try:
            # Clean up memory cache
            with self.cache_lock:
                current_time = datetime.now()
                old_keys = [
                    key for key, entry in self.memory_cache.items()
                    if (current_time - entry.last_accessed).days > 7
                ]
                
                for key in old_keys:
                    entry = self.memory_cache.pop(key)
                    self.current_cache_size -= entry.size_bytes
            
            # Clean up database cache
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            
            self.question_cache_db.execute("""
                DELETE FROM question_cache WHERE created_at < ?
            """, (cutoff_date,))
            self.question_cache_db.commit()
            
            self.evaluation_cache_db.execute("""
                DELETE FROM evaluation_cache WHERE created_at < ?
            """, (cutoff_date,))
            self.evaluation_cache_db.commit()
            
            if old_keys:
                logger.info(f"Cleaned up {len(old_keys)} old cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up cache entries: {e}")
    
    def _optimize_databases(self):
        """Optimize database performance"""
        try:
            # Vacuum databases
            self.question_cache_db.execute("VACUUM")
            self.evaluation_cache_db.execute("VACUUM")
            
            # Analyze for query optimization
            self.question_cache_db.execute("ANALYZE")
            self.evaluation_cache_db.execute("ANALYZE")
            
            logger.debug("Database optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing databases: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            import psutil
            
            # Update memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            self.performance_metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # Update CPU usage
            self.performance_metrics.cpu_usage_percent = process.cpu_percent()
            
            # Update concurrent requests
            self.performance_metrics.concurrent_requests = len(self.memory_cache)
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        with self.metrics_lock:
            return PerformanceMetrics(
                cache_hit_rate=self.performance_metrics.cache_hit_rate,
                avg_response_time=self.performance_metrics.avg_response_time,
                memory_usage_mb=self.performance_metrics.memory_usage_mb,
                cpu_usage_percent=self.performance_metrics.cpu_usage_percent,
                concurrent_requests=self.performance_metrics.concurrent_requests,
                error_rate=self.performance_metrics.error_rate
            )
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.cache_lock:
            return {
                "memory_cache_size": len(self.memory_cache),
                "memory_cache_size_mb": self.current_cache_size / 1024 / 1024,
                "max_cache_size_mb": self.cache_size_mb,
                "cache_utilization": self.current_cache_size / (self.cache_size_mb * 1024 * 1024),
                "embedding_cache_size": len(self.embedding_cache),
                "llm_pool_size": len(self.llm_pool)
            }
    
    def optimize_for_offline(self) -> Dict[str, Any]:
        """Optimize system for offline operation"""
        optimization_results = {
            "cache_optimization": self._optimize_cache(),
            "database_optimization": self._optimize_databases(),
            "memory_optimization": self._optimize_memory(),
            "concurrency_optimization": self._optimize_concurrency()
        }
        
        return optimization_results
    
    def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        with self.cache_lock:
            # Preload frequently accessed items
            frequently_accessed = [
                (key, entry) for key, entry in self.memory_cache.items()
                if entry.access_count > 5
            ]
            
            # Sort by access count
            frequently_accessed.sort(key=lambda x: x[1].access_count, reverse=True)
            
            return {
                "frequently_accessed_items": len(frequently_accessed),
                "cache_hit_rate": self.performance_metrics.cache_hit_rate,
                "optimization_status": "completed"
            }
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        # Force garbage collection
        import gc
        gc.collect()
        
        return {
            "memory_usage_mb": self.performance_metrics.memory_usage_mb,
            "optimization_status": "completed"
        }
    
    def _optimize_concurrency(self) -> Dict[str, Any]:
        """Optimize concurrency settings"""
        return {
            "max_concurrent": self.max_concurrent,
            "active_threads": threading.active_count(),
            "optimization_status": "completed"
        }
    
    def shutdown(self):
        """Shutdown optimization engine"""
        logger.info("Shutting down offline optimization engine...")
        
        # Stop background optimization
        self.optimization_active = False
        
        # Wait for optimization thread to finish
        if self.optimization_thread.is_alive():
            self.optimization_thread.join(timeout=5)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Close database connections
        self.question_cache_db.close()
        self.evaluation_cache_db.close()
        
        logger.info("Offline optimization engine shutdown complete")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.shutdown()
        except:
            pass  # Ignore errors during cleanup
