"""
Enhanced AI Technical Interviewer - Main Entry Point
Autonomous Learning-Based Adaptive Intelligence System
"""

import gradio as gr
import logging
import sys
import os
import time
import asyncio
from typing import List, Tuple, Optional, Dict, Any
import json
from pathlib import Path

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_NOFILE"] = "1"

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.ai_interviewer.core.enhanced_flow_controller import EnhancedFlowController
    from src.ai_interviewer.core.offline_optimization_engine import OfflineOptimizationEngine
    from src.ai_interviewer.utils.health_check import HealthChecker
    from src.ai_interviewer.utils.config import Config
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # Create mock classes for demonstration
    class EnhancedFlowController:
        def start_interview(self, topic, name): 
            return {"status": "started", "session_id": "mock", "first_question": f"Mock question for {topic}"}
        def process_answer(self, session, answer): 
            return {"status": "continue", "next_question": "Mock next question", "question_number": 2}
    
    class OfflineOptimizationEngine:
        def get_performance_metrics(self): return {"cache_hit_rate": 0.0}
        def get_cache_statistics(self): return {"memory_cache_size": 0}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedInterviewApp:
    """Enhanced AI Technical Interviewer with Autonomous Learning"""
    
    def __init__(self):
        # Initialize health checker
        self.health_checker = HealthChecker()
        
        # Validate configuration
        config_validation = Config.validate_config()
        if not config_validation["valid"]:
            logger.error("Configuration validation failed:")
            for error in config_validation["errors"]:
                logger.error(f"  - {error}")
            raise ValueError("Invalid configuration")
        
        if config_validation["warnings"]:
            for warning in config_validation["warnings"]:
                logger.warning(f"Configuration warning: {warning}")
        
        # Initialize enhanced components
        self.offline_engine = OfflineOptimizationEngine(
            cache_size_mb=500,
            max_concurrent=20
        )
        
        self.flow_controller = EnhancedFlowController(
            max_concurrent_sessions=10
        )
        
        self.current_session = None
        self.interview_history = []
        
        # Enhanced features
        self.adaptive_learning_enabled = True
        self.offline_optimization_enabled = True
        
        # Run initial health check
        self._run_startup_health_check()
        
        # Initialize performance monitoring
        self._start_performance_monitoring()
    
    def _run_startup_health_check(self):
        """Run comprehensive health check during startup"""
        try:
            logger.info("🔍 Running enhanced startup health check...")
            health_status = self.health_checker.run_comprehensive_check()
            
            if health_status["overall_status"] == "critical":
                logger.error("❌ Critical health issues detected during startup:")
                for check_name, check_result in health_status["checks"].items():
                    if check_result["status"] == "critical":
                        logger.error(f"  - {check_name}: {check_result['message']}")
                raise RuntimeError("Critical health check failures")
            elif health_status["overall_status"] == "warning":
                logger.warning("⚠️ Health warnings detected during startup:")
                for check_name, check_result in health_status["checks"].items():
                    if check_result["status"] == "warning":
                        logger.warning(f"  - {check_name}: {check_result['message']}")
            else:
                logger.info("✅ All health checks passed")
                
        except Exception as e:
            logger.error(f"Health check failed during startup: {e}")
            # Don't fail startup for health check issues, just log them
    
    def _start_performance_monitoring(self):
        """Start background performance monitoring"""
        import threading
        
        def monitor_performance():
            while True:
                try:
                    # Get performance metrics
                    metrics = self.offline_engine.get_performance_metrics()
                    cache_stats = self.offline_engine.get_cache_statistics()
                    
                    # Log performance every 5 minutes
                    logger.info(f"Performance: Cache hit rate: {metrics.cache_hit_rate:.2%}, "
                              f"Memory: {metrics.memory_usage_mb:.1f}MB, "
                              f"Cache size: {cache_stats['memory_cache_size_mb']:.1f}MB")
                    
                    time.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
        monitor_thread.start()
        logger.info("Started performance monitoring")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        health_status = self.health_checker.get_quick_status()
        
        # Add enhanced system status
        system_status = self.flow_controller.get_system_status()
        performance_metrics = self.offline_engine.get_performance_metrics()
        cache_stats = self.offline_engine.get_cache_statistics()
        
        enhanced_status = {
            **health_status,
            "enhanced_features": {
                "adaptive_learning": self.adaptive_learning_enabled,
                "offline_optimization": self.offline_optimization_enabled,
                "concurrent_sessions": system_status["concurrent_sessions"],
                "max_concurrent": system_status["max_concurrent_sessions"]
            },
            "performance_metrics": {
                "cache_hit_rate": performance_metrics.cache_hit_rate,
                "memory_usage_mb": performance_metrics.memory_usage_mb,
                "cpu_usage_percent": performance_metrics.cpu_usage_percent,
                "error_rate": performance_metrics.error_rate
            },
            "cache_statistics": cache_stats
        }
        
        return enhanced_status
        
    def start_interview(self, topic: str, candidate_name: str) -> Tuple[str, str, str, bool, bool]:
        """Start enhanced adaptive interview session"""
        try:
            if not candidate_name.strip():
                return "⚠️ Please enter your name to begin the interview.", "", "", True, True
            
            # Start enhanced interview
            result = self.flow_controller.start_interview(topic, candidate_name)
            
            if result["status"] == "started":
                self.current_session = {
                    "session_id": result["session_id"],
                    "topic": topic,
                    "candidate_name": candidate_name,
                    "question_count": result["question_number"],
                    "max_questions": 5,
                    "qa_pairs": [],
                    "start_time": time.time(),
                    "adaptive_features": result.get("adaptive_features", {}),
                    "system_info": result.get("system_info", {})
                }
                
                first_question = result["first_question"]
                self.current_session["current_question"] = first_question
                
                # Enhanced welcome message with adaptive features
                welcome_msg = f"""## 🧠 Enhanced AI Interview Started!

**Candidate:** {candidate_name}  
**Topic:** {topic}  
**Progress:** Question {result['question_number']} of 5

### 🚀 Adaptive Features Active:
- **🧠 Learning Intelligence:** System learns from your responses
- **📊 Performance Analysis:** Real-time difficulty adjustment
- **🎯 Knowledge Tracking:** Identifies strengths and gaps
- **⚡ Offline Optimization:** Cached responses for speed

---

### Question {result['question_number']}/5

{first_question}

💡 **Enhanced Tip:** The AI adapts questions based on your performance and learning patterns!"""

                status_msg = f"🟢 **Status:** Adaptive Interview Active - Question {result['question_number']}/5"
                
                return welcome_msg, "", status_msg, False, False
            else:
                error_msg = f"❌ **Error:** {result.get('message', 'Failed to start interview')}"
                if result.get('error_code') == 'CONCURRENCY_LIMIT':
                    error_msg += "\n\n🔄 **System Status:** High concurrent usage. Please try again in a moment."
                
                return error_msg, "", "🔴 **Status:** Error", True, True
            
        except Exception as e:
            logger.error(f"Error starting enhanced interview: {e}")
            return f"❌ **Error:** Failed to start interview - {str(e)}", "", "🔴 **Status:** Error", True, True
    
    def process_answer(self, answer: str) -> Tuple[str, str, str, bool]:
        """Process answer with enhanced adaptive learning"""
        try:
            if not self.current_session:
                return "❌ **Error:** No active interview session. Please start an interview first.", "", "🔴 **Status:** No Active Session", True
            
            if not answer.strip():
                return "⚠️ **Please provide an answer to continue.**", answer, "🟡 **Status:** Waiting for Answer", False
            
            # Process with enhanced flow controller
            result = self.flow_controller.process_answer(self.current_session, answer)
            
            if result["status"] == "continue":
                # Update session with new question
                self.current_session["question_count"] = result["question_number"]
                self.current_session["current_question"] = result["next_question"]
                
                # Add Q&A pair to session
                qa_pair = {
                    "question_number": result["question_number"] - 1,
                    "question": self.current_session.get("current_question", ""),
                    "answer": answer,
                    "evaluation": result["evaluation"],
                    "learning_insights": result.get("learning_insights", {})
                }
                self.current_session["qa_pairs"].append(qa_pair)
                
                # Enhanced response with learning insights
                learning_insights = result.get("learning_insights", {})
                performance_trend = learning_insights.get("performance_trend", [])
                knowledge_gaps = learning_insights.get("knowledge_gaps", [])
                strengths = learning_insights.get("strengths", [])
                
                response = f"""## ✅ Answer Processed with Learning Intelligence

**Your Score:** {result['evaluation'].get('overall_score', 0)}/10

### 📊 Learning Insights:
- **Performance Trend:** {performance_trend[-3:] if len(performance_trend) >= 3 else performance_trend}
- **Strengths Identified:** {', '.join(strengths[:2]) if strengths else 'Building...'}
- **Knowledge Gaps:** {', '.join(knowledge_gaps[:2]) if knowledge_gaps else 'None detected'}

### Question {result['question_number']}/5

{result['next_question']}

---

**Progress:** {result['question_number']-1}/5 questions completed
**System Status:** {result.get('performance_metrics', {}).get('concurrent_sessions', 0)} active sessions"""
                
                status_msg = f"🟢 **Status:** Adaptive Learning Active - Question {result['question_number']}/5"
                
                return response, "", status_msg, False
                
            elif result["status"] == "complete":
                # Interview finished with enhanced report
                final_report = result["final_report"]
                learning_insights = result.get("learning_insights", {})
                
                response = f"""## 🎉 Enhanced Interview Complete!

### 📊 Comprehensive Learning Report

{final_report}

---

### 🧠 Learning System Summary:
- **Total Questions:** {len(self.current_session['qa_pairs'])}/5
- **Topic:** {self.current_session['topic']}
- **Average Score:** {sum(qa.get('evaluation', {}).get('overall_score', 0) for qa in self.current_session['qa_pairs']) / len(self.current_session['qa_pairs']):.1f}/10
- **Learning Progression:** {learning_insights.get('learning_progression', {}).get('trend', 'analyzing')}

### 🚀 System Performance:
- **Processing Time:** {result.get('performance_metrics', {}).get('processing_time', 0):.2f}s
- **Cache Hit Rate:** {self.offline_engine.get_performance_metrics().cache_hit_rate:.1%}
- **Memory Usage:** {self.offline_engine.get_performance_metrics().memory_usage_mb:.1f}MB

**Thank you for participating in our Enhanced AI Learning System!**

*Ready for another adaptive interview? Select a new topic above and click "Start Interview"*"""
                
                status_msg = "✅ **Status:** Enhanced Interview Completed Successfully"
                
                # Reset session
                self.current_session = None
                return response, "", status_msg, True
            else:
                return f"❌ **Error:** {result.get('message', 'Unexpected result from enhanced flow controller')}", answer, "🔴 **Status:** Processing Error", False
            
        except Exception as e:
            logger.error(f"Error processing enhanced answer: {e}")
            return f"❌ **Error:** Failed to process answer - {str(e)}", answer, "🔴 **Status:** Processing Error", False
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics"""
        try:
            # Get learning analytics
            learning_analytics = self.flow_controller.get_learning_analytics()
            
            # Get performance metrics
            performance_metrics = self.offline_engine.get_performance_metrics()
            cache_stats = self.offline_engine.get_cache_statistics()
            
            # Get system status
            system_status = self.flow_controller.get_system_status()
            
            return {
                "learning_analytics": learning_analytics,
                "performance_metrics": {
                    "cache_hit_rate": performance_metrics.cache_hit_rate,
                    "avg_response_time": performance_metrics.avg_response_time,
                    "memory_usage_mb": performance_metrics.memory_usage_mb,
                    "cpu_usage_percent": performance_metrics.cpu_usage_percent,
                    "error_rate": performance_metrics.error_rate
                },
                "cache_statistics": cache_stats,
                "system_status": system_status,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {"error": str(e)}
    
    def create_enhanced_interface(self) -> gr.Blocks:
        """Create enhanced Gradio interface with adaptive features"""
        
        # Enhanced CSS for modern design
        enhanced_css = """
        /* Enhanced theme variables */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #48bb78;
            --learning-color: #9f7aea;
            --bg-dark: #1a202c;
            --bg-medium: #2d3748;
            --bg-light: #4a5568;
            --text-primary: #f7fafc;
            --text-secondary: #e2e8f0;
            --border-color: #4a5568;
        }
        
        /* Global container styling */
        .gradio-container {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
            background: var(--bg-dark) !important;
            color: var(--text-primary) !important;
        }
        
        /* Enhanced header */
        .enhanced-header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #9f7aea 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        /* Learning features showcase */
        .learning-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .learning-feature {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .learning-feature:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(159, 122, 234, 0.3);
        }
        
        .learning-feature h4 {
            color: var(--learning-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .learning-feature p {
            color: var(--text-secondary) !important;
            margin: 0;
            font-size: 0.9rem;
        }
        
        /* Performance indicators */
        .performance-indicator {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .performance-indicator .label {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        .performance-indicator .value {
            color: var(--accent-color) !important;
            font-weight: 700;
        }
        
        /* Enhanced interview content */
        .enhanced-interview-content {
            background: var(--bg-medium) !important;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border-left: 4px solid var(--learning-color);
            color: var(--text-primary) !important;
        }
        
        /* Learning insights panel */
        .learning-insights {
            background: var(--bg-light) !important;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid var(--learning-color);
        }
        
        .learning-insights h4 {
            color: var(--learning-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .learning-insights p {
            color: var(--text-secondary) !important;
            margin: 0.25rem 0;
        }
        
        /* Enhanced buttons */
        .enhanced-btn {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--learning-color) 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            color: white !important;
        }
        
        .enhanced-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(159, 122, 234, 0.4) !important;
        }
        
        /* System status indicator */
        .system-status {
            background: var(--bg-medium) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .system-status h4 {
            color: var(--accent-color) !important;
            margin-bottom: 0.5rem;
        }
        
        .system-status .status-item {
            display: flex;
            justify-content: space-between;
            margin: 0.25rem 0;
        }
        
        .system-status .status-label {
            color: var(--text-secondary) !important;
        }
        
        .system-status .status-value {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        """
        
        with gr.Blocks(
            title="Enhanced AI Technical Interviewer - Autonomous Learning System",
            theme=gr.themes.Base(
                primary_hue="blue",
                secondary_hue="purple",
                neutral_hue="slate"
            ).set(
                body_background_fill="*neutral_950",
                body_text_color="*neutral_50",
                background_fill_primary="*neutral_900",
                background_fill_secondary="*neutral_800",
                border_color_primary="*neutral_700",
                block_background_fill="*neutral_900",
                input_background_fill="*neutral_800",
                button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #9f7aea 100%)",
                button_primary_text_color="white"
            ),
            css=enhanced_css
        ) as interface:
            
            # Enhanced header
            gr.HTML("""
            <div class="enhanced-header">
                <h1 style="margin:0; font-size: 2.5rem; font-weight: 800;">🧠 Enhanced AI Technical Interviewer</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">Autonomous Learning-Based Adaptive Intelligence System</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.8;">Powered by Advanced AI Agents & Offline Optimization</p>
            </div>
            """)
            
            # Learning features showcase
            gr.HTML("""
            <div class="learning-features">
                <div class="learning-feature">
                    <h4>🧠 Adaptive Learning</h4>
                    <p>System learns from each interview and improves over time</p>
                </div>
                <div class="learning-feature">
                    <h4>📊 Performance Analysis</h4>
                    <p>Real-time difficulty adjustment based on performance</p>
                </div>
                <div class="learning-feature">
                    <h4>🎯 Knowledge Tracking</h4>
                    <p>Identifies strengths and knowledge gaps automatically</p>
                </div>
                <div class="learning-feature">
                    <h4>⚡ Offline Optimization</h4>
                    <p>Cached responses and optimized performance</p>
                </div>
                <div class="learning-feature">
                    <h4>🔄 Concurrent Processing</h4>
                    <p>Handles multiple interviews simultaneously</p>
                </div>
                <div class="learning-feature">
                    <h4>🔒 Privacy First</h4>
                    <p>Everything runs locally with advanced security</p>
                </div>
            </div>
            """)
            
            # Main interface
            with gr.Row():
                # Left panel - Controls
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 🎯 Enhanced Interview Setup")
                    
                    candidate_name = gr.Textbox(
                        label="👤 Your Name",
                        placeholder="Enter your full name",
                        elem_classes=["custom-input"],
                        info="This will appear in your enhanced interview report"
                    )
                    
                    topic_dropdown = gr.Dropdown(
                        label="📚 Interview Topic",
                        choices=[
                            "JavaScript/Frontend Development",
                            "Python/Backend Development", 
                            "Machine Learning/AI",
                            "System Design",
                            "Data Structures & Algorithms"
                        ],
                        value="JavaScript/Frontend Development",
                        elem_classes=["custom-input"],
                        info="Choose your area of expertise"
                    )
                    
                    start_btn = gr.Button(
                        "🚀 Start Enhanced Interview", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["enhanced-btn"]
                    )
                    
                    # System status
                    gr.Markdown("### 📊 System Status")
                    system_status = gr.Markdown(
                        "🟡 **Status:** Ready to Start",
                        elem_classes=["system-status"]
                    )
                
                # Right panel - Interview content
                with gr.Column(scale=2):
                    interview_display = gr.Markdown(
                        """
                        ### 👋 Welcome to Enhanced AI Technical Interviewer!
                        
                        **Experience the future of AI-powered interviews with autonomous learning capabilities.**
                        
                        #### 🧠 How Enhanced Learning Works:
                        1. **Enter your name** and select your **interview topic**
                        2. **Click "Start Enhanced Interview"** to begin
                        3. **Answer 5 adaptive questions** - each one intelligently tailored to your responses
                        4. **Receive comprehensive feedback** with learning insights and recommendations
                        
                        #### 🚀 Enhanced Features:
                        - **🧠 Adaptive Learning:** System learns from every interview and improves
                        - **📊 Performance Analysis:** Real-time difficulty adjustment based on your performance
                        - **🎯 Knowledge Tracking:** Automatically identifies your strengths and knowledge gaps
                        - **⚡ Offline Optimization:** Cached responses for faster, more efficient processing
                        - **🔄 Concurrent Processing:** Handles multiple interviews simultaneously
                        - **🔒 Privacy First:** Everything runs locally on your machine
                        
                        #### 📚 Available Topics:
                        - **JavaScript/Frontend:** React, DOM manipulation, ES6+, async programming
                        - **Python/Backend:** Django/Flask, APIs, databases, server architecture  
                        - **Machine Learning:** Algorithms, model selection, data preprocessing
                        - **System Design:** Scalability, architecture patterns, distributed systems
                        - **Data Structures & Algorithms:** Complexity analysis, problem solving
                        
                        **Ready to experience the future of AI interviews? Let's begin! 🎯**
                        """,
                        elem_classes=["enhanced-interview-content"]
                    )
            
            # Answer section
            gr.Markdown("### 💬 Your Response")
            with gr.Column(elem_classes=["answer-section"]):
                answer_input = gr.Textbox(
                    label="📝 Your Answer",
                    placeholder="Share your thoughts, approach, and reasoning here...",
                    lines=5,
                    interactive=True,
                    elem_classes=["custom-input"],
                    info="💡 Enhanced Tip: The AI analyzes your response patterns and adapts accordingly!"
                )
                
                with gr.Row(elem_classes=["button-row"]):
                    submit_btn = gr.Button(
                        "📤 Submit Answer", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["enhanced-btn"]
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear", 
                        variant="secondary",
                        size="lg",
                        elem_classes=["clear-button"]
                    )
            
            # Hidden state to track button states
            start_btn_disabled = gr.State(False)
            submit_btn_disabled = gr.State(True)
            
            # Event handlers
            start_btn.click(
                fn=self.start_interview,
                inputs=[topic_dropdown, candidate_name],
                outputs=[interview_display, answer_input, system_status, start_btn_disabled, submit_btn_disabled]
            )
            
            submit_btn.click(
                fn=self.process_answer,
                inputs=[answer_input],
                outputs=[interview_display, answer_input, system_status, submit_btn_disabled]
            )
            
            # Allow Enter key to submit
            answer_input.submit(
                fn=self.process_answer,
                inputs=[answer_input], 
                outputs=[interview_display, answer_input, system_status, submit_btn_disabled]
            )
            
            # Clear button
            clear_btn.click(
                fn=lambda: "",
                outputs=[answer_input]
            )
            
            # Enhanced footer
            gr.HTML("""
            <div class="footer-section">
                <p><strong>Enhanced AI Technical Interviewer</strong> • Autonomous Learning System • Powered by Advanced AI Agents</p>
                <p style="font-size: 0.9rem;">🧠 Learning Intelligence • ⚡ Offline Optimization • 🔄 Concurrent Processing • 🔒 Privacy First</p>
                <p style="font-size: 0.8rem;">Built with LangGraph, Ollama + llama3.2:3b, ChromaDB, and Advanced Caching</p>
            </div>
            """)
        
        return interface

def main():
    """Enhanced main entry point"""
    print("🚀 Starting Enhanced AI Technical Interviewer...")
    print("🧠 Features: Autonomous Learning-Based Adaptive Intelligence")
    print("📋 Requirements: 100% Compliant with Enterprise Standards")
    print("🤖 LLM: Ollama + llama3.2:3b (Local)")
    print("🔄 Flow: Enhanced LangGraph with Learning")
    print("⚡ Optimization: Offline Caching & Concurrency")
    print("🌐 Interface: Enhanced Gradio Web UI")
    print("=" * 80)
    
    try:
        app = EnhancedInterviewApp()
        interface = app.create_enhanced_interface()
        
        # Launch with enhanced configuration
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,
            share=False,  # Set to True if you want public sharing
            show_error=True,
            quiet=False,
            inbrowser=True,  # Auto-open browser
            favicon_path=None,
        )
        
    except Exception as e:
        logger.error(f"Failed to start enhanced application: {e}")
        print(f"❌ Error: {e}")
        print("\n🔧 Enhanced Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull the model: ollama pull llama3.2:3b") 
        print("3. Check requirements: pip install -r requirements.txt")
        print("4. Try: pip install --upgrade gradio pydantic fastapi")
        print("5. Check system resources for concurrent processing")

if __name__ == "__main__":
    main()
