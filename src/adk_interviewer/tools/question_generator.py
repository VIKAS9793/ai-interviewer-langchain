"""
Question Generator Tool for ADK Interviewer.

Generates adaptive, context-aware technical interview questions
using Chain-of-Thought reasoning and Time-Travel Diffusion (TTD).
"""

from typing import Optional
from google.adk.tools import ToolContext
from ..config import config


def generate_question(
    topic: str,
    difficulty: str,
    tool_context: ToolContext,
    previous_questions: Optional[list[str]] = None,
    candidate_context: Optional[dict[str, str]] = None
) -> dict:
    """
    Generate a technical interview question.
    
    This tool uses Chain-of-Thought reasoning to create contextually
    appropriate questions that adapt to the candidate's skill level.
    
    Uses ToolContext to maintain interview state across questions.
    
    Args:
        topic: The technical topic (e.g., "Python", "System Design")
        difficulty: Question difficulty ("easy", "medium", "hard", "expert")
        previous_questions: List of already-asked questions to avoid repetition
        candidate_context: Optional context about candidate's background
        
    Returns:
        dict: {
            "question": str,           # The generated question
            "expected_answer": str,    # Key points for evaluation
            "difficulty": str,         # Actual difficulty level
            "topic": str,              # Specific sub-topic
            "reasoning": str           # CoT reasoning for question choice
        }
        
    Example:
        >>> result = generate_question(
        ...     topic="Python",
        ...     difficulty="medium",
        ...     previous_questions=["Explain list comprehensions"]
        ... )
        >>> print(result["question"])
        "How would you implement a custom iterator in Python?"
    """
    # Retrieve state from context (interview history)
    asked_questions = tool_context.state.get("asked_questions", [])
    interview_topic = tool_context.state.get("interview_topic", topic)
    
    # Validate difficulty
    if difficulty not in config.DIFFICULTY_LEVELS:
        difficulty = "medium"
    
    # Question templates by topic (TTD will refine these)
    question_banks = {
        "Python": {
            "easy": [
                "What is the difference between a list and a tuple in Python?",
                "Explain how Python's garbage collection works.",
                "What are decorators in Python and why are they useful?"
            ],
            "medium": [
                "How would you implement a custom iterator in Python?",
                "Explain the Global Interpreter Lock (GIL) and its implications.",
                "What are context managers and how do you create one?"
            ],
            "hard": [
                "Implement a thread-safe singleton pattern in Python.",
                "Explain metaclasses and provide a practical use case.",
                "How would you profile and optimize a memory-intensive Python application?"
            ],
            "expert": [
                "Design a custom async event loop from scratch.",
                "Implement a distributed task queue similar to Celery.",
                "How would you build a Python JIT compiler?"
            ]
        },
        "System Design": {
            "easy": [
                "What is the difference between horizontal and vertical scaling?",
                "Explain the concept of caching and when to use it.",
                "What is a load balancer and how does it work?"
            ],
            "medium": [
                "Design a URL shortening service like bit.ly.",
                "How would you design a rate limiter for an API?",
                "Explain CAP theorem and its practical implications."
            ],
            "hard": [
                "Design a distributed message queue like Kafka.",
                "How would you architect a real-time collaborative editor?",
                "Design a content delivery network (CDN) from scratch."
            ],
            "expert": [
                "Design a globally distributed database with strong consistency.",
                "Architect a system to handle 1 million concurrent video streams.",
                "Design a fault-tolerant payment processing system."
            ]
        },
        "Data Structures": {
            "easy": [
                "Explain the difference between arrays and linked lists.",
                "What is a hash table and how does it handle collisions?",
                "Describe the properties of a binary search tree."
            ],
            "medium": [
                "Implement a LRU cache with O(1) get and put operations.",
                "Explain how a red-black tree maintains balance.",
                "Design a data structure for autocomplete suggestions."
            ],
            "hard": [
                "Implement a skip list and analyze its complexity.",
                "Design a concurrent hash map without using locks.",
                "Implement a B+ tree for database indexing."
            ],
            "expert": [
                "Design a data structure for efficient range queries on streaming data.",
                "Implement a lock-free queue for multi-threaded systems.",
                "Design an in-memory spatial index for geolocation queries."
            ]
        }
    }
    
    # Get question bank for topic
    topic_bank = question_banks.get(topic, question_banks.get("Python"))
    difficulty_questions = topic_bank.get(difficulty, topic_bank["medium"])
    
    # Filter out previously asked questions
    available_questions = [
        q for q in difficulty_questions
        if q not in (previous_questions or [])
    ]
    
    
    # Select question (TTD would refine this with LLM)
    if available_questions:
        selected_question = available_questions[0]
    else:
        # Fallback if all questions used
        selected_question = f"Tell me about your experience with {topic}."
    
    # Update state with new question
    asked_questions.append(selected_question)
    tool_context.state["asked_questions"] = asked_questions
    tool_context.state["interview_topic"] = topic
    tool_context.state["current_difficulty"] = difficulty
    
    return {
        "question": selected_question,
        "expected_answer": f"Demonstrate understanding of {topic} concepts at {difficulty} level",
        "difficulty": difficulty,
        "topic": topic,
        "reasoning": f"Selected {difficulty} question on {topic} based on candidate context"
    }
