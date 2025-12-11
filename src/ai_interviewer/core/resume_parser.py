import logging
import re
from typing import Optional, Dict, Any
import io

# Optional imports with graceful fallback
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import bleach
except ImportError:
    bleach = None

logger = logging.getLogger(__name__)

class ResumeParser:
    """
    Parses resume files (PDF/DOCX) and extracts text for analysis.
    Includes text sanitization security measures.
    """
    
    @staticmethod
    def extract_text(file_obj, filename: str) -> Optional[str]:
        """
        Extracts raw text from a file object.
        """
        try:
            filename = filename.lower()
            text = ""
            
            if filename.endswith('.pdf'):
                if not PdfReader:
                    logger.error("pypdf not installed")
                    return None
                reader = PdfReader(file_obj)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
            elif filename.endswith('.docx'):
                if not Document:
                    logger.error("python-docx not installed")
                    return None
                doc = Document(file_obj)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            
            if not text.strip():
                logger.warning("Extracted empty text from resume")
                return None
                
            return ResumeParser.sanitize_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing resume {filename}: {e}")
            return None

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitizes extracted text to prevent injection and reduce constraints.
        """
        if not text:
            return ""
            
        # 1. HTML Sanitization (if bleach is available)
        if bleach:
            text = bleach.clean(text, tags=[], attributes={}, strip=True)
            
        # 2. Normalize Whitespace
        # Replace multiple newlines/spaces with single space, but keep paragraph breaks
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 3. Remove non-printable characters (except standard ASCII/Unicode text)
        # Keep basic punctuation and alphanumeric
        text = "".join(ch for ch in text if ch.isprintable())
        
        # 4. Length Limit (Prevent Context Window overflow)
        # 20,000 chars is roughly 4-5k tokens, plenty for a resume
        return text[:20000]

    @staticmethod
    def analyze_content(text: str) -> Dict[str, Any]:
        """
        Basic heuristic analysis of resume content (Mock/Placeholder for LLM)
        In a real flow, this text goes to the LLM.
        """
        skills_keywords = ["python", "java", "javascript", "react", "node", "aws", "docker", "kubernetes", "sql", "nosql", "machine learning", "ai"]
        found_skills = [skill for skill in skills_keywords if skill in text.lower()]
        
        return {
            "text_length": len(text),
            "found_skills": list(set(found_skills))
        }
