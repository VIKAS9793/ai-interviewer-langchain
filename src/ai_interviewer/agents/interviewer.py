"""
AI Technical Interviewer - Core Logic
Professional technical interview simulation with intelligent question generation
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import OutputParserException
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)

class QuestionResponse(BaseModel):
    """Structured response for generated questions"""
    question: str = Field(description="The interview question")
    difficulty: str = Field(description="Question difficulty: easy, medium, hard")
    expected_concepts: List[str] = Field(description="Key concepts the answer should cover")
    follow_up_hints: List[str] = Field(description="Potential follow-up questions or hints")

class AnswerEvaluation(BaseModel):
    """Structured response for answer evaluation"""
    technical_accuracy: int = Field(description="Technical correctness score (1-10)")
    problem_solving: int = Field(description="Problem-solving approach score (1-10)")
    communication: int = Field(description="Communication clarity score (1-10)")
    depth: int = Field(description="Depth of understanding score (1-10)")
    overall_score: int = Field(description="Overall score (1-10)")
    strengths: List[str] = Field(description="Key strengths demonstrated")
    improvements: List[str] = Field(description="Areas for improvement")
    next_difficulty: str = Field(description="Recommended next question difficulty")

class AIInterviewer:
    """Main AI Interviewer class with professional questioning and evaluation"""
    
    def __init__(self):
        """Initialize the AI Interviewer with Ollama LLM"""
        try:
            # Initialize Ollama LLM (Local - no external APIs)
            from ..utils.config import Config
            self.llm = Ollama(
                model=Config.OLLAMA_MODEL,
                temperature=Config.OLLAMA_TEMPERATURE
            )
            
            # Test connection
            test_response = self.llm.invoke("Hello")
            logger.info("✅ Ollama connection established successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Ollama: {e}")
            raise ConnectionError(f"Ollama connection failed: {e}")
    
    def generate_first_question(self, topic: str) -> str:
        """Generate the first interview question for a given topic"""
        
        question_prompt = PromptTemplate(
            input_variables=["topic"],
            template="""You are a senior technical interviewer conducting a professional interview.

Topic: {topic}

Generate the FIRST question for a technical interview. This should be a warm-up question that:
- Tests fundamental knowledge
- Is not too difficult to start
- Allows the candidate to demonstrate their understanding
- Sets a professional tone

Return ONLY the question text, no additional formatting or explanation.

Question:"""
        )
        
        try:
            chain = question_prompt | self.llm
            question = chain.invoke({"topic": topic})
            return question.strip()
            
        except Exception as e:
            logger.error(f"Error generating first question: {e}")
            # Fallback questions by topic
            fallback_questions = {
                "JavaScript/Frontend Development": "Can you explain the difference between 'let', 'const', and 'var' in JavaScript?",
                "Python/Backend Development": "What is the difference between a list and a tuple in Python?",
                "Machine Learning/AI": "Can you explain what overfitting means in machine learning?",
                "System Design": "What factors would you consider when designing a scalable web application?",
                "Data Structures & Algorithms": "Can you explain the time complexity of different sorting algorithms?"
            }
            return fallback_questions.get(topic, "Tell me about your experience with programming.")
    
    def generate_next_question(self, topic: str, conversation_history: List[Dict], 
                             last_evaluation: Dict, question_number: int) -> str:
        """Generate the next question based on conversation history and performance"""
        
        # Determine difficulty based on last evaluation
        last_score = last_evaluation.get("overall_score", 5)
        if last_score >= 8:
            difficulty = "hard"
            follow_up_strategy = "challenge with advanced concepts"
        elif last_score >= 6:
            difficulty = "medium"
            follow_up_strategy = "explore breadth and practical application"
        else:
            difficulty = "easy"
            follow_up_strategy = "reinforce fundamentals and build confidence"
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPREVIOUS CONVERSATION:\n"
            for i, qa in enumerate(conversation_history, 1):
                conversation_context += f"Q{i}: {qa.get('question', '')[:100]}...\n"
                conversation_context += f"A{i}: {qa.get('answer', '')[:150]}...\n"
                evaluation = qa.get('evaluation', {})
                conversation_context += f"Score: {evaluation.get('overall_score', 0)}/10\n\n"
        
        # Get areas that need improvement or strengths to build on
        last_strengths = last_evaluation.get('strengths', [])
        last_improvements = last_evaluation.get('improvements', [])
        
        next_question_prompt = PromptTemplate(
            input_variables=["topic", "difficulty", "question_number", "conversation_context", 
                           "follow_up_strategy", "last_strengths", "last_improvements"],
            template="""You are a senior technical interviewer conducting an adaptive interview.

Topic: {topic}
Question Number: {question_number}/5
Difficulty Level: {difficulty}
Strategy: {follow_up_strategy}

Last Answer Analysis:
- Strengths: {last_strengths}
- Areas for Improvement: {last_improvements}

{conversation_context}

Based on the conversation history and the candidate's performance, generate the next question that:

1. **RESPONDS TO PREVIOUS ANSWERS**: Reference or build upon what they've already discussed
2. **ADAPTIVE DIFFICULTY**: Use {difficulty} level appropriate to their demonstrated skill
3. **STRATEGIC FOLLOW-UP**: {follow_up_strategy}
4. **NATURAL PROGRESSION**: Create logical flow from previous topics

Examples of good follow-ups:
- If they struggled with basic concepts → Ask simpler, foundational questions
- If they excelled → Challenge with edge cases or advanced scenarios
- If they mentioned specific technologies → Dive deeper into those areas
- If they showed gaps → Address those specific knowledge areas

Return ONLY the question text, no additional formatting.

Question:"""
        )
        
        try:
            chain = next_question_prompt | self.llm
            question = chain.invoke({
                "topic": topic,
                "difficulty": difficulty,
                "question_number": question_number,
                "conversation_context": conversation_context,
                "follow_up_strategy": follow_up_strategy,
                "last_strengths": ", ".join(last_strengths) if last_strengths else "None identified",
                "last_improvements": ", ".join(last_improvements) if last_improvements else "None identified"
            })
            return question.strip()
            
        except Exception as e:
            logger.error(f"Error generating next question: {e}")
            # Fallback based on difficulty and topic
            return self._get_fallback_question(topic, difficulty, question_number)
    
    def evaluate_answer(self, question: str, answer: str, topic: str) -> Dict[str, Any]:
        """Evaluate candidate's answer with professional scoring"""
        
        evaluation_prompt = PromptTemplate(
            input_variables=["question", "answer", "topic"],
            template="""You are a senior technical interviewer evaluating a candidate's answer.

Topic: {topic}
Question: {question}
Answer: {answer}

Evaluate this answer on a scale of 1-10 for each dimension:

1. Technical Accuracy (1-10): How technically correct is the answer?
2. Problem Solving (1-10): How well does it demonstrate problem-solving skills?
3. Communication (1-10): How clearly is the answer communicated?
4. Depth (1-10): How deep is the understanding demonstrated?

Also provide:
- Overall score (1-10)
- 2-3 key strengths
- 2-3 areas for improvement
- Recommended next difficulty (easy/medium/hard)

Format your response as JSON:
{{
    "technical_accuracy": <score>,
    "problem_solving": <score>,
    "communication": <score>,
    "depth": <score>,
    "overall_score": <score>,
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "next_difficulty": "medium"
}}"""
        )
        
        try:
            chain = evaluation_prompt | self.llm
            response = chain.invoke({
                "question": question,
                "answer": answer,
                "topic": topic
            })
            
            # Extract JSON from response (robust parsing)
            response_text = response.strip()
            
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                evaluation = json.loads(json_text)
                
                # Validate required fields
                required_fields = ['technical_accuracy', 'problem_solving', 'communication', 'depth', 'overall_score']
                if all(field in evaluation for field in required_fields):
                    return evaluation
                else:
                    logger.warning("Missing required fields in evaluation, using fallback")
                    return self._get_fallback_evaluation(answer)
            else:
                logger.warning("No valid JSON found in response, using fallback")
                return self._get_fallback_evaluation(answer)
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            # Fallback evaluation
            return self._get_fallback_evaluation(answer)
    
    def generate_final_report(self, session_data: Dict) -> str:
        """Generate comprehensive final interview report"""
        
        report_prompt = PromptTemplate(
            input_variables=["topic", "questions", "answers", "scores"],
            template="""Generate a professional interview summary report.

Topic: {topic}
Questions Asked: {questions}
Candidate Answers: {answers}
Scores: {scores}

Create a comprehensive report including:
1. Overall Performance Summary
2. Technical Strengths
3. Areas for Improvement
4. Recommendations for Growth
5. Final Assessment

Make it professional, constructive, and actionable.

Report:"""
        )
        
        try:
            # Prepare session data
            questions = [qa.get("question", "") for qa in session_data.get("qa_pairs", [])]
            answers = [qa.get("answer", "") for qa in session_data.get("qa_pairs", [])]
            scores = [qa.get("evaluation", {}).get("overall_score", 0) for qa in session_data.get("qa_pairs", [])]
            
            chain = report_prompt | self.llm
            report = chain.invoke({
                "topic": session_data.get("topic", "Technical Interview"),
                "questions": "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]),
                "answers": "\n".join([f"{i+1}. {a[:200]}..." for i, a in enumerate(answers)]),
                "scores": f"Average Score: {sum(scores)/len(scores) if scores else 0:.1f}/10"
            })
            
            return report.strip()
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            return self._get_fallback_report(session_data)
    
    def _get_fallback_question(self, topic: str, difficulty: str, question_number: int) -> str:
        """Fallback questions when LLM generation fails"""
        fallback_questions = {
            "JavaScript/Frontend Development": {
                "easy": "What is the purpose of the 'this' keyword in JavaScript?",
                "medium": "How would you implement debouncing in JavaScript?",
                "hard": "Explain the event loop and how it handles asynchronous operations."
            },
            "Python/Backend Development": {
                "easy": "What is the difference between a list and a dictionary in Python?",
                "medium": "How would you handle database connections in a Python web application?",
                "hard": "Explain Python's GIL and its impact on multi-threading."
            }
        }
        
        questions = fallback_questions.get(topic, {})
        return questions.get(difficulty, f"Tell me about a challenging {topic} problem you've solved.")
    
    def _get_fallback_evaluation(self, answer: str) -> Dict[str, Any]:
        """Fallback evaluation when LLM evaluation fails"""
        # Simple heuristic scoring based on answer length and keywords
        answer_length = len(answer.split())
        
        if answer_length > 50:
            base_score = 7
        elif answer_length > 20:
            base_score = 6
        else:
            base_score = 4
            
        return {
            "technical_accuracy": base_score,
            "problem_solving": base_score,
            "communication": base_score - 1,
            "depth": base_score,
            "overall_score": base_score,
            "strengths": ["Provided a response", "Attempted to answer"],
            "improvements": ["Could provide more detail", "Consider technical specifics"],
            "next_difficulty": "medium"
        }
    
    def _get_fallback_report(self, session_data: Dict) -> str:
        """Fallback report when LLM generation fails"""
        qa_pairs = session_data.get("qa_pairs", [])
        scores = [qa.get("evaluation", {}).get("overall_score", 0) for qa in qa_pairs]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return f"""
## Interview Summary Report

**Topic:** {session_data.get('topic', 'Technical Interview')}
**Candidate:** {session_data.get('candidate_name', 'Candidate')}
**Questions Completed:** {len(qa_pairs)}/5

### Overall Performance
- **Average Score:** {avg_score:.1f}/10
- **Questions Answered:** {len(qa_pairs)}

### Summary
The candidate completed {len(qa_pairs)} questions with an average score of {avg_score:.1f}/10. 
This demonstrates {'strong' if avg_score >= 7 else 'good' if avg_score >= 5 else 'developing'} technical knowledge.

### Recommendations
- Continue practicing technical concepts
- Focus on clear communication of solutions
- Consider additional study in areas of lower performance

*Thank you for participating in this technical interview!*
"""
