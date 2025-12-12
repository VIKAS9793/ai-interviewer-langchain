"""
Metacognitive Critic (Reflexion Loop)
Implemented using LangGraph

Cycles: Draft -> Critique -> Revise -> Critique -> ... -> Final
"""

import logging
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from .autonomous_reasoning_engine import AutonomousReasoningEngine, InterviewContext

logger = logging.getLogger(__name__)

class ReflexionState(TypedDict):
    """State for the Reflexion Graph"""
    draft: str
    critique: Dict[str, Any]
    feedback_history: List[str]
    iterations: int
    context: InterviewContext
    final_output: str

class ReflexionLoop:
    """
    Orchestrates the self-correction loop using LangGraph.
    
    Flow:
    1. Input: Initial Draft
    2. Node: Critique (Evaluate quality)
    3. Conditional: 
       - If Score >= 8: End
       - If Iterations > 3: End
       - Else: Revise
    4. Node: Revise (Rewrite based on feedback)
    5. Loop back to Critique
    """
    
    def __init__(self, reasoning_engine: AutonomousReasoningEngine):
        self.engine = reasoning_engine
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ReflexionState)
        
        # Add Nodes
        workflow.add_node("critique", self._critique_node)
        workflow.add_node("revise", self._revise_node)
        
        # Set Entry Point
        # We assume 'draft' is populated in initial state
        workflow.set_entry_point("critique")
        
        # Add Edges
        workflow.add_conditional_edges(
            "critique",
            self._should_continue,
            {
                "revise": "revise",
                "end": END
            }
        )
        workflow.add_edge("revise", "critique")
        
        return workflow.compile()

    def _critique_node(self, state: ReflexionState) -> Dict[str, Any]:
        """Node: Critique the current draft"""
        draft = state["draft"]
        context = state["context"]
        
        logger.info(f"🤔 Reflexion: Critiquing draft (Iter {state['iterations']})...")
        critique = self.engine.critique_draft(draft, context)
        
        return {
            "critique": critique,
            "iterations": state["iterations"] + 1,
            "final_output": draft # Update final output to current draft
        }

    def _revise_node(self, state: ReflexionState) -> Dict[str, Any]:
        """Node: Revise draft based on critique"""
        draft = state["draft"]
        critique = state["critique"]
        context = state["context"]
        
        logger.info(f"✏️ Reflexion: Revising draft (Score: {critique.get('score')})...")
        new_draft = self.engine.revise_draft(draft, critique, context)
        
        return {
            "draft": new_draft,
            "feedback_history": state["feedback_history"] + [critique.get("reasoning", "")]
        }

    def _should_continue(self, state: ReflexionState) -> str:
        """Edge Logic: Decide next step"""
        score = state["critique"].get("score", 0)
        iterations = state["iterations"]
        
        if score >= 8:
            logger.info("✅ Reflexion: Quality threshold met.")
            return "end"
        
        if iterations >= 3:
            logger.info("⚠️ Reflexion: Max iterations reached.")
            return "end"
            
        return "revise"

    def refine(self, initial_draft: str, context: InterviewContext) -> Dict[str, Any]:
        """Run the reflexion loop on a draft"""
        try:
            initial_state = {
                "draft": initial_draft,
                "critique": {},
                "feedback_history": [],
                "iterations": 0,
                "context": context,
                "final_output": initial_draft
            }
            
            final_state = self.graph.invoke(initial_state)
            return {
                "final_output": final_state["final_output"],
                "critique": final_state["critique"],
                "iterations": final_state["iterations"]
            }
        except Exception as e:
            logger.error(f"Reflexion loop failed: {e}")
            # Fallback to initial
            return {
                "final_output": initial_draft,
                "critique": {"score": 0, "error": str(e)},
                "iterations": 0
            }
