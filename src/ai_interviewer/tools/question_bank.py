"""
Question Bank Management - ChromaDB Vector Store Integration
Semantic question retrieval and management for AI interviews
"""

import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import json
import time

logger = logging.getLogger(__name__)

class QuestionBank:
    """Vector-based question bank using ChromaDB for semantic retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB vector store for questions"""
        try:
            # Initialize ChromaDB client with telemetry disabled
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Initialize sentence transformer for embeddings (will be loaded on demand)
            self.embedding_model = None
            
            # Get or create collections for different topics
            self.collections = {}
            self._initialize_collections()
            
            # Populate with initial questions if empty
            self._populate_initial_questions()
            
            logger.info("✅ QuestionBank initialized with ChromaDB")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize QuestionBank: {e}")
            raise
    
    def _get_embedding_model(self):
        """Lazy load the embedding model"""
        if self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Sentence transformer loaded")
            except ImportError:
                logger.warning("⚠️ Sentence transformers not available, using basic text matching")
                self.embedding_model = "basic"
        return self.embedding_model
    
    def _initialize_collections(self):
        """Initialize ChromaDB collections for different interview topics"""
        topics = [
            "javascript_frontend",
            "python_backend", 
            "machine_learning",
            "system_design",
            "algorithms"
        ]
        
        for topic in topics:
            try:
                collection = self.client.get_or_create_collection(
                    name=topic,
                    metadata={"description": f"Questions for {topic} interviews"}
                )
                self.collections[topic] = collection
                logger.info(f"Initialized collection: {topic}")
                
            except Exception as e:
                logger.error(f"Error initializing collection {topic}: {e}")
    
    def _populate_initial_questions(self):
        """Populate collections with initial question sets"""
        
        initial_questions = {
            "javascript_frontend": [
                {
                    "question": "Explain the difference between 'let', 'const', and 'var' in JavaScript.",
                    "difficulty": "easy",
                    "concepts": ["variables", "scope", "hoisting"],
                    "expected_answer": "var is function-scoped and hoisted, let is block-scoped, const is block-scoped and immutable"
                },
                {
                    "question": "How does JavaScript's event loop work?",
                    "difficulty": "hard", 
                    "concepts": ["event loop", "asynchronous", "callbacks"],
                    "expected_answer": "Event loop manages execution of code, collecting and processing events, and executing queued sub-tasks"
                },
                {
                    "question": "What is the difference between == and === in JavaScript?",
                    "difficulty": "easy",
                    "concepts": ["equality", "type coercion"],
                    "expected_answer": "== performs type coercion, === checks both value and type"
                },
                {
                    "question": "Explain closures in JavaScript with an example.",
                    "difficulty": "medium",
                    "concepts": ["closures", "scope", "functions"],
                    "expected_answer": "A closure gives access to outer function's scope from inner function"
                },
                {
                    "question": "How would you implement debouncing in JavaScript?",
                    "difficulty": "medium",
                    "concepts": ["debouncing", "performance", "events"],
                    "expected_answer": "Use setTimeout to delay function execution and clearTimeout to cancel previous calls"
                }
            ],
            
            "python_backend": [
                {
                    "question": "What is the difference between a list and a tuple in Python?",
                    "difficulty": "easy",
                    "concepts": ["data structures", "mutability"],
                    "expected_answer": "Lists are mutable and use [], tuples are immutable and use ()"
                },
                {
                    "question": "Explain Python's GIL and its impact on multi-threading.",
                    "difficulty": "hard",
                    "concepts": ["GIL", "threading", "performance"],
                    "expected_answer": "Global Interpreter Lock prevents multiple threads from executing Python code simultaneously"
                },
                {
                    "question": "How do you handle exceptions in Python?",
                    "difficulty": "easy",
                    "concepts": ["exceptions", "error handling"],
                    "expected_answer": "Use try/except blocks to catch and handle exceptions"
                },
                {
                    "question": "What are Python decorators and how do you use them?",
                    "difficulty": "medium",
                    "concepts": ["decorators", "functions", "metaprogramming"],
                    "expected_answer": "Functions that modify or extend behavior of other functions"
                },
                {
                    "question": "How would you optimize a slow database query in a Python web application?",
                    "difficulty": "medium",
                    "concepts": ["database", "optimization", "performance"],
                    "expected_answer": "Add indexes, optimize queries, use connection pooling, implement caching"
                }
            ],
            
            "machine_learning": [
                {
                    "question": "What is overfitting in machine learning and how do you prevent it?",
                    "difficulty": "easy",
                    "concepts": ["overfitting", "generalization", "validation"],
                    "expected_answer": "Model performs well on training data but poorly on new data. Prevent with regularization, cross-validation, more data"
                },
                {
                    "question": "Explain the bias-variance tradeoff.",
                    "difficulty": "medium",
                    "concepts": ["bias", "variance", "model complexity"],
                    "expected_answer": "Bias is error from oversimplification, variance is error from sensitivity to small fluctuations"
                },
                {
                    "question": "How do you evaluate a machine learning model?",
                    "difficulty": "easy",
                    "concepts": ["evaluation", "metrics", "validation"],
                    "expected_answer": "Use metrics like accuracy, precision, recall, F1-score, and cross-validation"
                },
                {
                    "question": "What is the difference between supervised and unsupervised learning?",
                    "difficulty": "easy",
                    "concepts": ["supervised", "unsupervised", "learning types"],
                    "expected_answer": "Supervised uses labeled data, unsupervised finds patterns in unlabeled data"
                },
                {
                    "question": "Explain how gradient descent works.",
                    "difficulty": "medium",
                    "concepts": ["gradient descent", "optimization", "learning"],
                    "expected_answer": "Iterative optimization algorithm that finds minimum of function by following negative gradient"
                }
            ],
            
            "system_design": [
                {
                    "question": "How would you design a URL shortener like bit.ly?",
                    "difficulty": "medium",
                    "concepts": ["system design", "scalability", "databases"],
                    "expected_answer": "Use hash function or base62 encoding, database for mapping, caching, load balancing"
                },
                {
                    "question": "What factors do you consider when designing a scalable web application?",
                    "difficulty": "easy",
                    "concepts": ["scalability", "architecture", "performance"],
                    "expected_answer": "Load balancing, caching, database optimization, microservices, monitoring"
                },
                {
                    "question": "Explain the CAP theorem.",
                    "difficulty": "hard",
                    "concepts": ["CAP theorem", "distributed systems", "consistency"],
                    "expected_answer": "Can't simultaneously guarantee Consistency, Availability, and Partition tolerance"
                },
                {
                    "question": "How would you handle database scaling?",
                    "difficulty": "medium",
                    "concepts": ["database", "scaling", "sharding"],
                    "expected_answer": "Vertical scaling, horizontal scaling, sharding, read replicas, caching"
                },
                {
                    "question": "What is the difference between SQL and NoSQL databases?",
                    "difficulty": "easy",
                    "concepts": ["SQL", "NoSQL", "databases"],
                    "expected_answer": "SQL is relational with ACID properties, NoSQL is flexible with eventual consistency"
                }
            ],
            
            "algorithms": [
                {
                    "question": "Explain the time complexity of different sorting algorithms.",
                    "difficulty": "easy",
                    "concepts": ["sorting", "time complexity", "algorithms"],
                    "expected_answer": "Bubble sort O(n²), merge sort O(n log n), quick sort average O(n log n)"
                },
                {
                    "question": "How would you detect a cycle in a linked list?",
                    "difficulty": "medium",
                    "concepts": ["linked list", "cycle detection", "algorithms"],
                    "expected_answer": "Use Floyd's cycle detection algorithm with two pointers (slow and fast)"
                },
                {
                    "question": "What is dynamic programming and when would you use it?",
                    "difficulty": "medium",
                    "concepts": ["dynamic programming", "optimization", "algorithms"],
                    "expected_answer": "Technique for solving problems by breaking into subproblems and storing results"
                },
                {
                    "question": "Explain binary search and its time complexity.",
                    "difficulty": "easy",
                    "concepts": ["binary search", "time complexity", "algorithms"],
                    "expected_answer": "Search algorithm that divides sorted array in half, O(log n) time complexity"
                },
                {
                    "question": "How would you find the shortest path in a graph?",
                    "difficulty": "medium",
                    "concepts": ["graphs", "shortest path", "algorithms"],
                    "expected_answer": "Use Dijkstra's algorithm for weighted graphs, BFS for unweighted graphs"
                }
            ]
        }
        
        # Add questions to collections if they're empty
        for topic, questions in initial_questions.items():
            if topic in self.collections:
                collection = self.collections[topic]
                
                # Check if collection is empty
                if collection.count() == 0:
                    self._add_questions_to_collection(collection, questions)
                    logger.info(f"Populated {topic} with {len(questions)} questions")
    
    def _add_questions_to_collection(self, collection, questions: List[Dict]):
        """Add questions to a ChromaDB collection"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, q in enumerate(questions):
                documents.append(q["question"])
                metadatas.append({
                    "difficulty": q["difficulty"],
                    "concepts": json.dumps(q["concepts"]),
                    "expected_answer": q["expected_answer"]
                })
                ids.append(f"q_{i}")
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            logger.error(f"Error adding questions to collection: {e}")
    
    def get_questions_by_topic(self, topic: str, difficulty: Optional[str] = None, 
                              limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve questions by topic and difficulty"""
        try:
            # Map topic names to collection names
            topic_mapping = {
                "JavaScript/Frontend Development": "javascript_frontend",
                "Python/Backend Development": "python_backend",
                "Machine Learning/AI": "machine_learning", 
                "System Design": "system_design",
                "Data Structures & Algorithms": "algorithms"
            }
            
            collection_name = topic_mapping.get(topic, "javascript_frontend")
            
            if collection_name not in self.collections:
                logger.warning(f"Collection {collection_name} not found")
                return []
            
            collection = self.collections[collection_name]
            
            # Build query filters
            where_filter = {}
            if difficulty:
                where_filter["difficulty"] = difficulty
            
            # Query the collection
            results = collection.query(
                query_texts=[f"questions about {topic}"],
                n_results=limit,
                where=where_filter if where_filter else None
            )
            
            # Format results
            questions = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    questions.append({
                        "question": doc,
                        "difficulty": metadata.get("difficulty", "medium"),
                        "concepts": json.loads(metadata.get("concepts", "[]")),
                        "expected_answer": metadata.get("expected_answer", "")
                    })
            
            return questions
            
        except Exception as e:
            logger.error(f"Error retrieving questions: {e}")
            return []
    
    def search_similar_questions(self, query: str, topic: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search for questions similar to a given query"""
        try:
            topic_mapping = {
                "JavaScript/Frontend Development": "javascript_frontend",
                "Python/Backend Development": "python_backend", 
                "Machine Learning/AI": "machine_learning",
                "System Design": "system_design",
                "Data Structures & Algorithms": "algorithms"
            }
            
            collection_name = topic_mapping.get(topic, "javascript_frontend")
            
            if collection_name not in self.collections:
                return []
            
            collection = self.collections[collection_name]
            
            # Semantic search using the query
            results = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # Format results
            questions = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    questions.append({
                        "question": doc,
                        "difficulty": metadata.get("difficulty", "medium"),
                        "concepts": json.loads(metadata.get("concepts", "[]")),
                        "expected_answer": metadata.get("expected_answer", ""),
                        "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            return questions
            
        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            return []
    
    def add_custom_question(self, topic: str, question: str, difficulty: str, 
                           concepts: List[str], expected_answer: str) -> bool:
        """Add a custom question to the question bank"""
        try:
            topic_mapping = {
                "JavaScript/Frontend Development": "javascript_frontend",
                "Python/Backend Development": "python_backend",
                "Machine Learning/AI": "machine_learning",
                "System Design": "system_design", 
                "Data Structures & Algorithms": "algorithms"
            }
            
            collection_name = topic_mapping.get(topic, "javascript_frontend")
            
            if collection_name not in self.collections:
                return False
            
            collection = self.collections[collection_name]
            
            # Generate unique ID
            question_id = f"custom_{int(time.time())}"
            
            # Add to collection
            collection.add(
                documents=[question],
                metadatas=[{
                    "difficulty": difficulty,
                    "concepts": json.dumps(concepts),
                    "expected_answer": expected_answer,
                    "custom": True
                }],
                ids=[question_id]
            )
            
            logger.info(f"Added custom question to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom question: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about question collections"""
        stats = {}
        for name, collection in self.collections.items():
            try:
                stats[name] = collection.count()
            except Exception as e:
                logger.error(f"Error getting stats for {name}: {e}")
                stats[name] = 0
        
        return stats
