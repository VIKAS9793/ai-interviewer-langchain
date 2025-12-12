from locust import HttpUser, task, between
import json

class IDPUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def load_interface(self):
        """Simulate loading the main page"""
        self.client.get("/")

    @task(3)
    def submit_chat(self):
        """Simulate a chat interaction via Gradio API"""
        # Note: Gradio 4.x uses /gradio_api/call/...
        headers = {"Content-Type": "application/json"}
        
        # Payload for a typical chat prediction (simplified)
        # In real load testing, you'd match the exact /predict payload
        payload = {
            "data": ["Explain the event loop"],
            "fn_index": 0, # Placeholder index
            "session_hash": "test_session"
        }
        
        # We target the queue join which is standard for Gradio
        self.client.post("/gradio_api/queue/join", json=payload, headers=headers)
