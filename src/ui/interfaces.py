from typing import Protocol, Any, Dict, Tuple

class InterviewApp(Protocol):
    """Protocol defining the interface expected by the UI"""
    
    def start_topic_interview(self, topic: str, candidate_name: str) -> Tuple[Any, ...]:
        ...

    def start_practice_interview(
        self, 
        resume_file: Any, 
        jd_text: str, 
        jd_url: str, 
        candidate_name: str
    ) -> Tuple[Any, ...]:
        ...

    def process_answer(self, text: str, transcription: str) -> Tuple[Any, ...]:
        ...

    def transcribe_audio(self, audio: Any) -> str:
        ...
