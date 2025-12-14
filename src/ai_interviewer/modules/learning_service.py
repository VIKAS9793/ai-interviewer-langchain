"""
ReasoningBank: Self-Evolving Memory System for AI Interviewer

This module implements a memory framework for learning from interview experiences.
It distills strategies from both successful and failed interviews into structured
memory items that can be retrieved and applied to future interviews.

Research Reference:
    [1] "ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory"
        arXiv:2509.25140 (2025)
        https://arxiv.org/abs/2509.25140
    
    [2] "Learning on the Job: An Experience-Driven, Self-Evolving Agent"
        arXiv:2510.08002 (2025)
        https://arxiv.org/abs/2510.08002
"""

import logging
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import sqlite3
from contextlib import contextmanager

try:
    from huggingface_hub import HfApi, hf_hub_download
    from huggingface_hub.utils import RepositoryNotFoundError, RevisionNotFoundError
    HF_Hub_Available = True
except ImportError:
    HF_Hub_Available = False

logger = logging.getLogger(__name__)

class HuggingFacePersistence:
    """
    Persistence layer for HuggingFace Spaces.
    
    Synchronizes local SQLite memory bank with a private Dataset on HF Hub.
    Strategy:
    1. On Init: Download 'memory.db' from Hub to local ephemeral storage.
    2. On Save: Upload 'memory.db' to Hub (periodically or on trigger).
    
    Requires: HF_TOKEN in environment variables.
    """
    
    def __init__(self, repo_id: str, filename: str = "reasoning_bank.db"):
        self.repo_id = repo_id
        self.filename = filename
        self.api = HfApi()
        self.token = os.getenv("HF_TOKEN")
        
        if not self.token:
            logger.warning("⚠️ HF_TOKEN not found. Persistence disabled.")
            self.enabled = False
        else:
            self.enabled = True
            
    def sync_down(self, local_path: Path) -> bool:
        """Download remote DB to local path."""
        if not self.enabled: return False
        
        try:
            logger.info(f"⬇️ Syncing memory from {self.repo_id}...")
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                repo_type="dataset",
                local_dir=str(local_path.parent),
                local_dir_use_symlinks=False
            )
            logger.info("✅ Memory sync complete")
            return True
        except (RepositoryNotFoundError, RevisionNotFoundError):
            logger.info("🆕 Remote memory not found. Starting fresh.")
            return False
        except Exception as e:
            logger.error(f"❌ Memory sync failed: {e}")
            return False
            
    def sync_up(self, local_path: Path):
        """Upload local DB to remote Hub."""
        if not self.enabled: return
        
        try:
            logger.info(f"⬆️ pushing memory to {self.repo_id}...")
            self.api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=self.filename,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Auto-save procedural memory: {datetime.now().isoformat()}"
            )
            logger.info("✅ Memory push complete")
        except Exception as e:
            logger.error(f"❌ Memory push failed: {e}")


@dataclass
class MemoryItem:
    """
    Structured knowledge unit for interview strategies.
    
    Based on ReasoningBank's memory schema:
    - title: Concise identifier summarizing the core strategy
    - description: One-sentence summary of the memory item
    - content: Distilled reasoning steps and decision rationales
    
    Reference: arXiv:2509.25140, Section 3.2 "Memory Schema"
    """
    title: str
    description: str
    content: str
    source_type: str  # "success" or "failure"
    topic: str = ""
    confidence: float = 0.5
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        return cls(**data)
    
    def get_id(self) -> str:
        """Generate unique ID from title hash"""
        return hashlib.md5(self.title.encode()).hexdigest()[:12]


@dataclass
class SkillModule:
    """
    Procedural Memory Unit: A learned behavior sequence.
    
    Unlike declarative MemoryItem (text knowledge), a SkillModule
    is an executable pattern of thought:
    Trigger -> [Action Sequence] -> Outcome
    """
    skill_id: str
    trigger_context: str
    action_chain: List[str]
    success_rate: float = 0.5
    usage_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_memory_item(self) -> MemoryItem:
        """Convert skill to storage format (MemoryItem)"""
        return MemoryItem(
            title=f"[SKILL] {self.trigger_context}",
            description="Learned procedural skill module",
            content=json.dumps(self.action_chain),
            source_type="skill_module",
            topic="procedural",
            confidence=self.success_rate,
            usage_count=self.usage_count,
            created_at=self.created_at
        )


@dataclass
class InterviewTrajectory:
    """
    Complete record of an interview session for memory extraction.
    
    Based on MUSE's trajectory concept for experience distillation.
    Reference: arXiv:2510.08002, Section 3.1
    """
    session_id: str
    candidate_name: str
    topic: str
    questions: List[Dict[str, Any]]
    answers: List[Dict[str, Any]]
    evaluations: List[Dict[str, Any]]
    final_score: float
    success: bool  # Based on score threshold or candidate feedback
    strategies_used: List[str] = field(default_factory=list)
    challenges_faced: List[str] = field(default_factory=list)
    resolution_patterns: List[str] = field(default_factory=list)


class ReasoningBank:
    """
    Memory system for self-evolving interview strategies.
    
    Implements a closed-loop learning process:
    1. Retrieve - Find relevant memories for current context
    2. Execute - Use memories to guide interview
    3. Construct - Extract new memories from completed interview
    4. Consolidate - Merge and prune memory items
    
    Research Reference: arXiv:2509.25140 "ReasoningBank"
    """
    
    def __init__(self, db_path: str = "./data/memory/reasoning_bank.db"):
        """Initialize the ReasoningBank memory system."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize Remote Persistence
        self.persistence = None
        if os.getenv("HF_TOKEN") and HF_Hub_Available:
            repo_id = os.getenv("HF_MEMORY_REPO", "VIKAS9793/ai-interviewer-memory")
            self.persistence = HuggingFacePersistence(repo_id=repo_id)
            # Sync Down on startup
            self.persistence.sync_down(self.db_path)
            
        self._init_database()
        
        # In-memory cache for fast retrieval
        self._memory_cache: Dict[str, MemoryItem] = {}
        self._load_cache()
        
        logger.info(
            f"🧠 ReasoningBank initialized with {len(self._memory_cache)} memories"
        )
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory storage."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    topic TEXT,
                    confidence REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT,
                    last_used TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trajectories (
                    session_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    processed INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic ON memory_items(topic)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_source ON memory_items(source_type)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _load_cache(self):
        """Load all memories into cache for fast retrieval."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM memory_items").fetchall()
            for row in rows:
                item = MemoryItem(
                    title=row['title'],
                    description=row['description'],
                    content=row['content'],
                    source_type=row['source_type'],
                    topic=row['topic'] or "",
                    confidence=row['confidence'],
                    usage_count=row['usage_count'],
                    created_at=row['created_at'],
                    last_used=row['last_used']
                )
                self._memory_cache[row['id']] = item
    
    # =========================================================================
    # RETRIEVE: Find relevant memories for current context
    # =========================================================================
    
    def retrieve(
        self, 
        context: str, 
        topic: str = "", 
        k: int = 5,
        include_failures: bool = True
    ) -> List[MemoryItem]:
        """
        Retrieve top-k relevant memories for current interview context.
        
        Uses keyword matching for simplicity; can be enhanced with embeddings.
        
        Args:
            context: Current interview context/question
            topic: Interview topic for filtering
            k: Number of memories to retrieve
            include_failures: Whether to include failure lessons
            
        Returns:
            List of relevant MemoryItems
        
        Reference: arXiv:2509.25140, Section 3.2 "Memory Retrieval"
        """
        candidates = []
        context_lower = context.lower()
        context_words = set(context_lower.split())
        
        for item_id, item in self._memory_cache.items():
            # Filter by topic if specified
            if topic and item.topic and topic.lower() != item.topic.lower():
                continue
            
            # Filter failures if not requested
            if not include_failures and item.source_type == "failure":
                continue
            
            # Calculate relevance score (keyword overlap)
            item_words = set(item.title.lower().split() + 
                           item.description.lower().split())
            overlap = len(context_words & item_words)
            
            # Boost by confidence and usage
            score = overlap * (0.5 + item.confidence * 0.5)
            
            if score > 0 or not context_words:  # Include all if no context
                candidates.append((score, item))
        
        # Sort by relevance and return top-k
        candidates.sort(key=lambda x: x[0], reverse=True)
        results = [item for _, item in candidates[:k]]
        
        # Update usage stats
        for item in results:
            self._update_usage(item.get_id())
        
        logger.debug(f"📚 Retrieved {len(results)} memories for context")
        return results
    
    def _update_usage(self, item_id: str):
        """Update usage count and last_used timestamp."""
        if item_id in self._memory_cache:
            self._memory_cache[item_id].usage_count += 1
            self._memory_cache[item_id].last_used = datetime.now().isoformat()
            
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE memory_items 
                    SET usage_count = usage_count + 1, last_used = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), item_id))
                conn.commit()
    
    def sync(self):
        """Force synchronization with remote hub."""
        if self.persistence:
            self.persistence.sync_up(self.db_path)

    def save_skill(self, skill: SkillModule):
        """Save a functional skill module."""
        self.add_memory(skill.to_memory_item())

    # =========================================================================
    # CONSTRUCT: Extract memories from completed interviews
    # =========================================================================
    
    def store_trajectory(self, trajectory: InterviewTrajectory):
        """
        Store interview trajectory for later processing.
        
        Reference: arXiv:2510.08002, Section 3.4 "Memory Update Mechanism"
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO trajectories (session_id, data, processed, created_at)
                VALUES (?, ?, 0, ?)
            """, (trajectory.session_id, json.dumps(asdict(trajectory)), 
                  datetime.now().isoformat()))
            conn.commit()
        
        logger.info(f"📝 Stored trajectory {trajectory.session_id}")
    
    def distill_memories(self, trajectory: InterviewTrajectory) -> List[MemoryItem]:
        """
        Extract memory items from interview trajectory.
        
        Distills both success strategies and failure lessons.
        """
        memories = []
        
        if trajectory.success:
            # Extract success strategies
            memories.extend(self._extract_success_strategies(trajectory))
        else:
            # Extract failure lessons
            memories.extend(self._extract_failure_lessons(trajectory))
        
        # Store all extracted memories
        for memory in memories:
            self.add_memory(memory)
            
        # Auto-sync after significant update
        if self.persistence and memories:
            logger.info("☁️ Triggering cloud sync for new memories...")
            self.sync()
        
        logger.info(
            f"💡 Distilled {len(memories)} memories from trajectory "
            f"({trajectory.session_id})"
        )
        return memories
    
    def _extract_success_strategies(
        self, 
        trajectory: InterviewTrajectory
    ) -> List[MemoryItem]:
        """Extract validated strategies from successful interview."""
        strategies = []
        
        # Strategy 1: Effective difficulty progression
        if len(trajectory.evaluations) >= 3:
            scores = [e.get('overall_score', 5) for e in trajectory.evaluations]
            if all(s >= 6 for s in scores):
                strategies.append(MemoryItem(
                    title=f"Progressive difficulty for {trajectory.topic}",
                    description=(
                        f"Successful {trajectory.topic} interview with "
                        f"progressive difficulty"
                    ),
                    content=(
                        f"When interviewing for {trajectory.topic}, use progressive "
                        f"difficulty: start with fundamentals, then advance to "
                        f"complex topics. Average score achieved: "
                        f"{sum(scores)/len(scores):.1f}"
                    ),
                    source_type="success",
                    topic=trajectory.topic,
                    confidence=0.8
                ))
        
        # Strategy 2: Topic-specific approach
        for pattern in trajectory.resolution_patterns:
            strategies.append(MemoryItem(
                title=f"Resolution pattern: {pattern[:50]}",
                description=f"Effective pattern for {trajectory.topic}",
                content=pattern,
                source_type="success",
                topic=trajectory.topic,
                confidence=0.7
            ))
        
        return strategies
    
    def _extract_failure_lessons(
        self, 
        trajectory: InterviewTrajectory
    ) -> List[MemoryItem]:
        """Extract lessons from failed interview."""
        lessons = []
        
        # Lesson 1: Identify what went wrong
        for challenge in trajectory.challenges_faced:
            lessons.append(MemoryItem(
                title=f"Avoid: {challenge[:50]}",
                description=f"Challenge faced in {trajectory.topic} interview",
                content=(
                    f"When interviewing for {trajectory.topic}, avoid: {challenge}. "
                    f"This led to lower scores."
                ),
                source_type="failure",
                topic=trajectory.topic,
                confidence=0.6
            ))
        
        # Lesson 2: Low-scoring question patterns
        low_scores = [
            (i, e) for i, e in enumerate(trajectory.evaluations)
            if e.get('overall_score', 5) < 4
        ]
        for idx, eval_data in low_scores:
            if idx < len(trajectory.questions):
                q = trajectory.questions[idx]
                lessons.append(MemoryItem(
                    title=f"Difficult question pattern in {trajectory.topic}",
                    description="Question that led to low candidate score",
                    content=(
                        f"Question: {q.get('question', 'N/A')[:100]}... "
                        f"resulted in low score. Consider rephrasing or "
                        f"providing more context."
                    ),
                    source_type="failure",
                    topic=trajectory.topic,
                    confidence=0.5
                ))
        
        return lessons
    
    # =========================================================================
    # CONSOLIDATE: Merge and prune memories
    # =========================================================================
    
    def add_memory(self, memory: MemoryItem):
        """Add a new memory item to the bank."""
        item_id = memory.get_id()
        
        # Check for duplicate
        if item_id in self._memory_cache:
            # Update confidence for existing memory
            existing = self._memory_cache[item_id]
            existing.confidence = min(1.0, existing.confidence + 0.1)
            self._save_memory(existing)
            logger.debug(f"↑ Boosted confidence for: {memory.title[:50]}")
        else:
            self._memory_cache[item_id] = memory
            self._save_memory(memory)
            logger.debug(f"+ Added new memory: {memory.title[:50]}")
    
    def _save_memory(self, memory: MemoryItem):
        """Save memory to database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memory_items 
                (id, title, description, content, source_type, topic, 
                 confidence, usage_count, created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.get_id(),
                memory.title,
                memory.description,
                memory.content,
                memory.source_type,
                memory.topic,
                memory.confidence,
                memory.usage_count,
                memory.created_at,
                memory.last_used
            ))
            conn.commit()
    
    def consolidate(self, similarity_threshold: float = 0.7):
        """
        Consolidate memories: merge similar items, prune low-value ones.
        
        Reference: arXiv:2509.25140, Section 3.2 "Memory Consolidation"
        """
        # Prune low-confidence, rarely-used memories
        to_remove = []
        for item_id, item in self._memory_cache.items():
            if item.confidence < 0.3 and item.usage_count < 2:
                to_remove.append(item_id)
        
        for item_id in to_remove:
            self._remove_memory(item_id)
        
        logger.info(f"🧹 Consolidation: removed {len(to_remove)} low-value memories")
    
    def _remove_memory(self, item_id: str):
        """Remove a memory from cache and database."""
        if item_id in self._memory_cache:
            del self._memory_cache[item_id]
        
        with self._get_connection() as conn:
            conn.execute("DELETE FROM memory_items WHERE id = ?", (item_id,))
            conn.commit()
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory bank statistics."""
        success_count = sum(
            1 for m in self._memory_cache.values() 
            if m.source_type == "success"
        )
        failure_count = len(self._memory_cache) - success_count
        
        topics = {}
        for memory in self._memory_cache.values():
            topic = memory.topic or "general"
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            "total_memories": len(self._memory_cache),
            "success_strategies": success_count,
            "failure_lessons": failure_count,
            "topics": topics,
            "avg_confidence": sum(m.confidence for m in self._memory_cache.values()) 
                             / max(1, len(self._memory_cache))
        }
    
    def format_for_prompt(self, memories: List[MemoryItem]) -> str:
        """Format memories for LLM prompt injection."""
        if not memories:
            return ""
        
        lines = ["## Relevant Interview Strategies:\n"]
        
        for i, memory in enumerate(memories, 1):
            icon = "✅" if memory.source_type == "success" else "⚠️"
            lines.append(f"{icon} **{memory.title}**")
            lines.append(f"   {memory.content}\n")
        
        return "\n".join(lines)
