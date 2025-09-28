"""
LLM Connection Pool for AI Interviewer
Efficient connection management and pooling
"""

import logging
import threading
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from queue import Queue, Empty
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class ConnectionStats:
    """Connection pool statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0

class LLMConnection:
    """Individual LLM connection wrapper"""
    
    def __init__(self, connection_id: str, llm_instance):
        self.connection_id = connection_id
        self.llm_instance = llm_instance
        self.created_at = time.time()
        self.last_used = time.time()
        self.request_count = 0
        self.is_healthy = True
        self.lock = threading.Lock()
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt"""
        with self.lock:
            try:
                start_time = time.time()
                response = self.llm_instance.invoke(prompt)
                response_time = (time.time() - start_time) * 1000
                
                self.last_used = time.time()
                self.request_count += 1
                
                logger.debug(f"Connection {self.connection_id} processed request in {response_time:.2f}ms")
                return response
                
            except Exception as e:
                logger.error(f"Connection {self.connection_id} failed: {e}")
                self.is_healthy = False
                raise
    
    def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            test_response = self.llm_instance.invoke("Hello")
            self.is_healthy = bool(test_response and len(test_response.strip()) > 0)
            return self.is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for connection {self.connection_id}: {e}")
            self.is_healthy = False
            return False
    
    def get_age_seconds(self) -> float:
        """Get connection age in seconds"""
        return time.time() - self.created_at
    
    def get_idle_seconds(self) -> float:
        """Get idle time in seconds"""
        return time.time() - self.last_used

class LLMConnectionPool:
    """Connection pool for LLM instances"""
    
    def __init__(self, max_connections: int = 3, min_connections: int = 1, 
                 connection_timeout: int = 30, health_check_interval: int = 300):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.health_check_interval = health_check_interval
        
        self._pool: Queue = Queue(maxsize=max_connections)
        self._all_connections: Dict[str, LLMConnection] = {}
        self._stats = ConnectionStats()
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._running = False
        
        # Initialize minimum connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with minimum connections"""
        logger.info(f"Initializing LLM connection pool with {self.min_connections} connections")
        
        for i in range(self.min_connections):
            try:
                connection = self._create_connection()
                if connection:
                    self._pool.put(connection)
                    self._all_connections[connection.connection_id] = connection
                    self._stats.total_connections += 1
            except Exception as e:
                logger.error(f"Failed to create initial connection {i}: {e}")
        
        # Start cleanup thread
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"Connection pool initialized with {self._stats.total_connections} connections")
    
    def _create_connection(self) -> Optional[LLMConnection]:
        """Create a new LLM connection"""
        try:
            from langchain_community.llms import Ollama
            from ..utils.config import Config
            
            connection_id = f"conn_{int(time.time() * 1000)}_{len(self._all_connections)}"
            
            llm_instance = Ollama(
                model=Config.OLLAMA_MODEL,
                temperature=Config.OLLAMA_TEMPERATURE,
                base_url=Config.OLLAMA_BASE_URL
            )
            
            # Test the connection
            test_response = llm_instance.invoke("Hello")
            if not test_response or len(test_response.strip()) == 0:
                raise ConnectionError("LLM returned empty test response")
            
            connection = LLMConnection(connection_id, llm_instance)
            logger.info(f"Created new LLM connection: {connection_id}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create LLM connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)"""
        connection = None
        try:
            # Try to get existing connection
            try:
                connection = self._pool.get(timeout=self.connection_timeout)
            except Empty:
                # Create new connection if pool is empty and under limit
                with self._lock:
                    if self._stats.total_connections < self.max_connections:
                        connection = self._create_connection()
                        if connection:
                            self._all_connections[connection.connection_id] = connection
                            self._stats.total_connections += 1
                    else:
                        raise RuntimeError("Connection pool exhausted")
            
            if not connection:
                raise RuntimeError("Failed to obtain connection")
            
            # Health check
            if not connection.health_check():
                logger.warning(f"Connection {connection.connection_id} failed health check, creating new one")
                connection = self._create_connection()
                if not connection:
                    raise RuntimeError("Failed to create replacement connection")
            
            self._stats.active_connections += 1
            self._stats.total_requests += 1
            
            yield connection
            
            self._stats.successful_requests += 1
            
        except Exception as e:
            self._stats.failed_requests += 1
            logger.error(f"Connection error: {e}")
            raise
        finally:
            if connection:
                self._stats.active_connections -= 1
                # Return connection to pool if it's still healthy
                if connection.is_healthy and self._pool.qsize() < self.max_connections:
                    try:
                        self._pool.put_nowait(connection)
                    except:
                        # Pool is full, close the connection
                        self._close_connection(connection)
                else:
                    self._close_connection(connection)
    
    def _close_connection(self, connection: LLMConnection):
        """Close and remove a connection"""
        try:
            if connection.connection_id in self._all_connections:
                del self._all_connections[connection.connection_id]
                self._stats.total_connections -= 1
                logger.info(f"Closed connection: {connection.connection_id}")
        except Exception as e:
            logger.error(f"Error closing connection {connection.connection_id}: {e}")
    
    def _cleanup_worker(self):
        """Background worker for connection cleanup"""
        while self._running:
            try:
                time.sleep(self.health_check_interval)
                self._cleanup_connections()
            except Exception as e:
                logger.error(f"Error in cleanup worker: {e}")
    
    def _cleanup_connections(self):
        """Clean up unhealthy or old connections"""
        with self._lock:
            connections_to_remove = []
            
            for connection_id, connection in self._all_connections.items():
                # Remove unhealthy connections
                if not connection.is_healthy:
                    connections_to_remove.append(connection_id)
                    continue
                
                # Remove old connections (older than 1 hour)
                if connection.get_age_seconds() > 3600:
                    connections_to_remove.append(connection_id)
                    continue
                
                # Health check for idle connections
                if connection.get_idle_seconds() > self.health_check_interval:
                    if not connection.health_check():
                        connections_to_remove.append(connection_id)
            
            # Remove identified connections
            for connection_id in connections_to_remove:
                connection = self._all_connections.get(connection_id)
                if connection:
                    self._close_connection(connection)
            
            # Ensure minimum connections
            while self._stats.total_connections < self.min_connections:
                new_connection = self._create_connection()
                if new_connection:
                    self._all_connections[new_connection.connection_id] = new_connection
                    self._stats.total_connections += 1
                    try:
                        self._pool.put_nowait(new_connection)
                    except:
                        pass  # Pool might be full
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            self._stats.idle_connections = self._pool.qsize()
            
            # Calculate average response time
            if self._stats.successful_requests > 0:
                total_time = sum(
                    conn.request_count for conn in self._all_connections.values()
                )
                self._stats.avg_response_time_ms = total_time / self._stats.successful_requests
            
            return {
                "total_connections": self._stats.total_connections,
                "active_connections": self._stats.active_connections,
                "idle_connections": self._stats.idle_connections,
                "total_requests": self._stats.total_requests,
                "successful_requests": self._stats.successful_requests,
                "failed_requests": self._stats.failed_requests,
                "success_rate": (
                    self._stats.successful_requests / self._stats.total_requests 
                    if self._stats.total_requests > 0 else 0
                ),
                "avg_response_time_ms": self._stats.avg_response_time_ms,
                "pool_utilization": (
                    (self._stats.total_connections - self._stats.idle_connections) / 
                    self._stats.total_connections if self._stats.total_connections > 0 else 0
                )
            }
    
    def shutdown(self):
        """Shutdown the connection pool"""
        logger.info("Shutting down LLM connection pool...")
        self._running = False
        
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        
        # Close all connections
        with self._lock:
            for connection in list(self._all_connections.values()):
                self._close_connection(connection)
        
        logger.info("LLM connection pool shutdown complete")

# Global connection pool instance
_connection_pool: Optional[LLMConnectionPool] = None

def get_connection_pool() -> LLMConnectionPool:
    """Get the global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = LLMConnectionPool()
    return _connection_pool

def shutdown_connection_pool():
    """Shutdown the global connection pool"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.shutdown()
        _connection_pool = None
