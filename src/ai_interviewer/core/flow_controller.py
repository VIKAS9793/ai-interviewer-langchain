"""
Interview Flow Controller - LangGraph Implementation
Intelligent branching logic and state management for AI interviews
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
import time

logger = logging.getLogger(__name__)

class InterviewState(TypedDict):
    """State structure for the interview flow"""
    session_id: str
    candidate_name: str
    topic: str
    current_question_number: int
    max_questions: int
    qa_pairs: List[Dict[str, Any]]
    current_question: str
    current_answer: str
    last_evaluation: Dict[str, Any]
    interview_complete: bool
    start_time: float
    
class InterviewFlowController:
    """LangGraph-based flow controller for intelligent interview progression"""
    
    def __init__(self):
        """Initialize the flow controller with LangGraph state machine"""
        # Remove interviewer initialization to avoid circular imports
        self.graph = self._build_interview_graph()
        self.active_sessions: Dict[str, Dict] = {}
    
    def _build_interview_graph(self):
        """Build the LangGraph state machine for interview flow"""
        
        # Create the state graph
        workflow = StateGraph(InterviewState)
        
        # Add nodes for each interview stage
        workflow.add_node("start_interview", self._start_interview_node)
        workflow.add_node("ask_question", self._ask_question_node)
        workflow.add_node("evaluate_answer", self._evaluate_answer_node)
        workflow.add_node("decide_next", self._decide_next_node)
        workflow.add_node("generate_report", self._generate_report_node)
        
        # Define the flow edges
        workflow.set_entry_point("start_interview")
        
        # From start_interview -> ask_question
        workflow.add_edge("start_interview", "ask_question")
        
        # From ask_question -> evaluate_answer (after receiving answer)
        workflow.add_edge("ask_question", "evaluate_answer")
        
        # From evaluate_answer -> decide_next
        workflow.add_edge("evaluate_answer", "decide_next")
        
        # From decide_next -> either ask_question (continue) or generate_report (end)
        workflow.add_conditional_edges(
            "decide_next",
            self._should_continue_interview,
            {
                "continue": "ask_question",
                "complete": "generate_report"
            }
        )
        
        # From generate_report -> END
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    def start_interview(self, topic: str, candidate_name: str) -> Dict[str, Any]:
        """Start a new interview session"""
        try:
            session_id = f"{candidate_name}_{int(time.time())}"
            
            # Initialize interview state
            initial_state: InterviewState = {
                "session_id": session_id,
                "candidate_name": candidate_name,
                "topic": topic,
                "current_question_number": 1,
                "max_questions": 5,
                "qa_pairs": [],
                "current_question": "",
                "current_answer": "",
                "last_evaluation": {},
                "interview_complete": False,
                "start_time": time.time()
            }
            
            # Run the graph to start the interview
            result = self.graph.invoke(initial_state)
            
            # Store session
            self.active_sessions[session_id] = result
            
            logger.info(f"✅ Interview started for {candidate_name} on topic: {topic}")
            
            return {
                "session_id": session_id,
                "status": "started",
                "first_question": result["current_question"],
                "question_number": 1
            }
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            raise
    
    def process_answer(self, session: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Process candidate answer and determine next step"""
        try:
            session_id = session["session_id"]
            
            if session_id not in self.active_sessions:
                raise ValueError("Invalid session ID")
            
            current_state = self.active_sessions[session_id]
            
            # Update state with the answer
            current_state["current_answer"] = answer
            
            # Continue the graph execution from evaluate_answer
            updated_state = self._evaluate_answer_node(current_state)
            updated_state = self._decide_next_node(updated_state)
            
            # Check if interview should continue
            if self._should_continue_interview(updated_state) == "continue":
                # Generate next question
                updated_state = self._ask_question_node(updated_state)
                
                # Update session
                self.active_sessions[session_id] = updated_state
                
                return {
                    "status": "continue",
                    "next_question": updated_state["current_question"],
                    "question_number": updated_state["current_question_number"],
                    "evaluation": updated_state["last_evaluation"]
                }
            else:
                # Interview complete
                updated_state = self._generate_report_node(updated_state)
                
                # Update session
                self.active_sessions[session_id] = updated_state
                
                return {
                    "status": "complete",
                    "final_report": updated_state.get("final_report", ""),
                    "session_data": updated_state
                }
                
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            raise
    
    def _start_interview_node(self, state: InterviewState) -> InterviewState:
        """Initialize the interview session"""
        logger.info(f"Starting interview for {state['candidate_name']} on {state['topic']}")
        return state
    
    def _ask_question_node(self, state: InterviewState) -> InterviewState:
        """Generate and ask the next question"""
        try:
            # Import here to avoid circular imports
            from ..agents.interviewer import AIInterviewer
            interviewer = AIInterviewer()
            
            if state["current_question_number"] == 1:
                # First question
                question = interviewer.generate_first_question(state["topic"])
            else:
                # Subsequent questions based on conversation history
                question = interviewer.generate_next_question(
                    topic=state["topic"],
                    conversation_history=state["qa_pairs"],
                    last_evaluation=state["last_evaluation"],
                    question_number=state["current_question_number"]
                )
            
            state["current_question"] = question
            logger.info(f"Generated question {state['current_question_number']}: {question[:100]}...")
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            # Fallback question
            state["current_question"] = f"Can you tell me about your experience with {state['topic']}?"
            return state
    
    def _evaluate_answer_node(self, state: InterviewState) -> InterviewState:
        """Evaluate the candidate's answer"""
        try:
            # Import here to avoid circular imports
            from ..agents.interviewer import AIInterviewer
            interviewer = AIInterviewer()
            
            evaluation = interviewer.evaluate_answer(
                question=state["current_question"],
                answer=state["current_answer"],
                topic=state["topic"]
            )
            
            # Store the Q&A pair with evaluation
            qa_pair = {
                "question_number": state["current_question_number"],
                "question": state["current_question"],
                "answer": state["current_answer"],
                "evaluation": evaluation
            }
            
            state["qa_pairs"].append(qa_pair)
            state["last_evaluation"] = evaluation
            
            logger.info(f"Evaluated answer {state['current_question_number']}: Score {evaluation.get('overall_score', 0)}/10")
            
            return state
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            # Fallback evaluation
            fallback_eval = {
                "overall_score": 5,
                "technical_accuracy": 5,
                "problem_solving": 5,
                "communication": 5,
                "depth": 5,
                "strengths": ["Provided an answer"],
                "improvements": ["Could provide more detail"],
                "next_difficulty": "medium"
            }
            
            qa_pair = {
                "question_number": state["current_question_number"],
                "question": state["current_question"],
                "answer": state["current_answer"],
                "evaluation": fallback_eval
            }
            
            state["qa_pairs"].append(qa_pair)
            state["last_evaluation"] = fallback_eval
            
            return state
    
    def _decide_next_node(self, state: InterviewState) -> InterviewState:
        """Decide whether to continue or end the interview"""
        # Increment question number for next iteration
        state["current_question_number"] += 1
        
        # Check if we've reached the maximum questions
        if state["current_question_number"] > state["max_questions"]:
            state["interview_complete"] = True
        
        return state
    
    def _should_continue_interview(self, state: InterviewState) -> str:
        """Determine if interview should continue or complete"""
        if state["interview_complete"] or state["current_question_number"] > state["max_questions"]:
            return "complete"
        else:
            return "continue"
    
    def _generate_report_node(self, state: InterviewState) -> InterviewState:
        """Generate the final interview report"""
        try:
            # Import here to avoid circular imports
            from ..agents.interviewer import AIInterviewer
            interviewer = AIInterviewer()
            
            final_report = interviewer.generate_final_report(state)
            state["final_report"] = final_report
            
            # Calculate interview duration
            duration = time.time() - state["start_time"]
            state["duration_minutes"] = duration / 60
            
            logger.info(f"Generated final report for {state['candidate_name']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            # Fallback report
            state["final_report"] = f"""
## Interview Summary

**Candidate:** {state['candidate_name']}
**Topic:** {state['topic']}
**Questions Completed:** {len(state['qa_pairs'])}/5

The interview has been completed. Thank you for your participation!
"""
            return state
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an interview session"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End and cleanup an interview session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session {session_id} ended and cleaned up")
            return True
        return False
