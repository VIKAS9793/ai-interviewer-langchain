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
        Heuristic analysis of resume content to extract skills, experience level, and target role.
        """
        text_lower = text.lower()
        
        # Expanded skills list
        skills_keywords = [
            # Languages
            "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "php", "swift", "kotlin",
            # Frontend
            "react", "vue", "angular", "nextjs", "html", "css", "tailwind",
            # Backend
            "node", "django", "flask", "fastapi", "spring", "express",
            # Cloud & DevOps
            "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
            # Data
            "sql", "nosql", "mongodb", "postgresql", "redis", "elasticsearch",
            # AI/ML
            "machine learning", "deep learning", "ai", "tensorflow", "pytorch", "nlp", "computer vision",
            # Other
            "git", "agile", "scrum", "api", "rest", "graphql", "microservices"
        ]
        found_skills = [skill for skill in skills_keywords if skill in text_lower]
        
        # Role/Title extraction (look for common patterns)
        role_keywords = {
            "product manager": "Product Management",
            "software engineer": "Software Engineering", 
            "data scientist": "Data Science",
            "machine learning": "Machine Learning",
            "frontend": "Frontend Development",
            "backend": "Backend Development",
            "full stack": "Full Stack Development",
            "devops": "DevOps Engineering",
            "cloud engineer": "Cloud Engineering",
            "sre": "Site Reliability Engineering"
        }
        detected_role = "General Technical Interview"
        for keyword, role in role_keywords.items():
            if keyword in text_lower:
                detected_role = role
                break
        
        # Experience level detection
        experience_level = "Mid"
        if any(word in text_lower for word in ["senior", "lead", "principal", "staff", "director"]):
            experience_level = "Senior"
        elif any(word in text_lower for word in ["junior", "intern", "entry", "graduate", "fresher"]):
            experience_level = "Junior"
        
        return {
            "text_length": len(text),
            "found_skills": list(set(found_skills)),
            "detected_role": detected_role,
            "experience_level": experience_level
        }
