"""
Health Check System for AI Interviewer
Comprehensive monitoring and diagnostics
"""

import logging
import time
import psutil
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    response_time_ms: Optional[float] = None

class HealthChecker:
    """Comprehensive health check system"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks_performed = 0
        self.last_check_time = None
    
    def check_ollama_connection(self) -> HealthCheckResult:
        """Check Ollama LLM connection"""
        start_time = time.time()
        
        try:
            from ..utils.config import Config
            
            # Test basic connection
            response = requests.get(
                f"{Config.OLLAMA_BASE_URL}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                if Config.OLLAMA_MODEL in model_names:
                    response_time = (time.time() - start_time) * 1000
                    return HealthCheckResult(
                        status=HealthStatus.HEALTHY,
                        message=f"Ollama connected, model {Config.OLLAMA_MODEL} available",
                        details={
                            "base_url": Config.OLLAMA_BASE_URL,
                            "model": Config.OLLAMA_MODEL,
                            "available_models": len(model_names)
                        },
                        response_time_ms=response_time
                    )
                else:
                    return HealthCheckResult(
                        status=HealthStatus.CRITICAL,
                        message=f"Model {Config.OLLAMA_MODEL} not found in Ollama",
                        details={
                            "base_url": Config.OLLAMA_BASE_URL,
                            "expected_model": Config.OLLAMA_MODEL,
                            "available_models": model_names
                        }
                    )
            else:
                return HealthCheckResult(
                    status=HealthStatus.CRITICAL,
                    message=f"Ollama API returned status {response.status_code}",
                    details={"base_url": Config.OLLAMA_BASE_URL, "status_code": response.status_code}
                )
                
        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                message="Cannot connect to Ollama service",
                details={"base_url": Config.OLLAMA_BASE_URL}
            )
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                status=HealthStatus.WARNING,
                message="Ollama connection timeout",
                details={"base_url": Config.OLLAMA_BASE_URL}
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                message=f"Ollama check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_chromadb_status(self) -> HealthCheckResult:
        """Check ChromaDB vector store status"""
        start_time = time.time()
        
        try:
            import chromadb
            from ..utils.config import Config
            
            # Test ChromaDB connection
            client = chromadb.PersistentClient(
                path=Config.CHROMADB_PERSIST_DIRECTORY,
                settings=chromadb.config.Settings(anonymized_telemetry=False)
            )
            
            # Get collections
            collections = client.list_collections()
            collection_count = len(collections)
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"ChromaDB connected with {collection_count} collections",
                details={
                    "persist_directory": Config.CHROMADB_PERSIST_DIRECTORY,
                    "collection_count": collection_count,
                    "collections": [col.name for col in collections]
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                message=f"ChromaDB check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # Determine status
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 70:
                status = HealthStatus.WARNING
                warnings.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
            
            if memory_percent > 90:
                status = HealthStatus.CRITICAL
                warnings.append(f"High memory usage: {memory_percent:.1f}%")
            elif memory_percent > 80:
                status = HealthStatus.WARNING
                warnings.append(f"Elevated memory usage: {memory_percent:.1f}%")
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                warnings.append(f"Low disk space: {disk_percent:.1f}% used")
            elif disk_percent > 85:
                status = HealthStatus.WARNING
                warnings.append(f"Elevated disk usage: {disk_percent:.1f}%")
            
            message = "System resources normal"
            if warnings:
                message = "; ".join(warnings)
            
            return HealthCheckResult(
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_available_gb": round(memory_available_gb, 2),
                    "disk_percent": disk_percent,
                    "disk_free_gb": round(disk_free_gb, 2)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message=f"System resource check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_application_status(self) -> HealthCheckResult:
        """Check application-specific status"""
        try:
            uptime_seconds = time.time() - self.start_time
            uptime_hours = uptime_seconds / 3600
            
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message=f"Application running for {uptime_hours:.1f} hours",
                details={
                    "uptime_seconds": uptime_seconds,
                    "uptime_hours": uptime_hours,
                    "checks_performed": self.checks_performed,
                    "last_check": self.last_check_time
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                message=f"Application status check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        self.checks_performed += 1
        self.last_check_time = time.time()
        
        checks = {
            "ollama": self.check_ollama_connection(),
            "chromadb": self.check_chromadb_status(),
            "system_resources": self.check_system_resources(),
            "application": self.check_application_status()
        }
        
        # Determine overall status
        statuses = [check.status for check in checks.values()]
        
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate response time
        total_response_time = sum(
            check.response_time_ms for check in checks.values() 
            if check.response_time_ms is not None
        )
        
        return {
            "overall_status": overall_status.value,
            "timestamp": time.time(),
            "response_time_ms": total_response_time,
            "checks": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details,
                    "response_time_ms": check.response_time_ms
                }
                for name, check in checks.items()
            }
        }
    
    def get_quick_status(self) -> Dict[str, Any]:
        """Get a quick status overview"""
        try:
            ollama_check = self.check_ollama_connection()
            system_check = self.check_system_resources()
            
            return {
                "status": "healthy" if ollama_check.status == HealthStatus.HEALTHY else "degraded",
                "ollama": ollama_check.status.value,
                "system": system_check.status.value,
                "uptime_hours": (time.time() - self.start_time) / 3600
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
