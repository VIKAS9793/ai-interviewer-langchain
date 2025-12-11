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
        Uses word boundary matching to avoid false positives.
        """
        import re
        text_lower = text.lower()
        
        # Skills with word boundary matching to avoid false positives
        tech_skills = [
            # Languages (use word boundaries)
            r"\bpython\b", r"\bjava\b", r"\bjavascript\b", r"\btypescript\b", 
            r"\bgolang\b", r"\brust\b", r"\bc\+\+\b", r"\bc#\b", r"\bruby\b", 
            r"\bphp\b", r"\bswift\b", r"\bkotlin\b",
            # Frontend
            r"\breact\b", r"\bvue\b", r"\bangular\b", r"\bnextjs\b", r"\bnext\.js\b",
            # Backend
            r"\bnode\.?js\b", r"\bdjango\b", r"\bflask\b", r"\bfastapi\b", r"\bspring\b",
            # Cloud & DevOps
            r"\baws\b", r"\bgcp\b", r"\bazure\b", r"\bdocker\b", r"\bkubernetes\b", 
            r"\bterraform\b", r"\bjenkins\b", r"\bci/cd\b",
            # Data
            r"\bsql\b", r"\bnosql\b", r"\bmongodb\b", r"\bpostgresql\b", r"\bredis\b",
            # AI/ML
            r"\bmachine learning\b", r"\bdeep learning\b", r"\btensorflow\b", 
            r"\bpytorch\b", r"\bnlp\b", r"\bcomputer vision\b",
        ]
        
        # Business/Sales skills (for non-technical roles)
        business_skills = [
            r"\bcrm\b", r"\bsalesforce\b", r"\bsales\b", r"\baccount management\b",
            r"\brelationship management\b", r"\bbusiness development\b", 
            r"\bconsultative selling\b", r"\bpipeline\b", r"\bnegotiation\b",
            r"\bportfolio management\b", r"\baum\b", r"\basset management\b",
            r"\bwealth management\b", r"\bbanking\b", r"\bfinance\b",
            r"\bproject management\b", r"\bproduct management\b", r"\bagile\b", r"\bscrum\b",
        ]
        
        # Find matches with word boundaries
        found_tech = [skill.replace(r"\b", "").replace("\\", "") 
                      for skill in tech_skills if re.search(skill, text_lower)]
        found_business = [skill.replace(r"\b", "").replace("\\", "") 
                          for skill in business_skills if re.search(skill, text_lower)]
        all_skills = list(set(found_tech + found_business))
        
        # Role detection with priority
        role_keywords = [
            (r"business pro", "Business Development"),
            (r"business development", "Business Development"),
            (r"relationship manager", "Relationship Management"),
            (r"sales", "Sales"),
            (r"product manager", "Product Management"),
            (r"project manager", "Project Management"),
            (r"software engineer", "Software Engineering"),
            (r"data scientist", "Data Science"),
            (r"machine learning", "Machine Learning"),
            (r"devops", "DevOps Engineering"),
        ]
        detected_role = "General Interview"
        for pattern, role in role_keywords:
            if re.search(pattern, text_lower):
                detected_role = role
                break
        
        # Experience level detection - look for years of experience
        experience_level = "Mid"
        years_match = re.search(r"(\d+)\+?\s*years?\s*(of)?\s*(experience|exp)?", text_lower)
        if years_match:
            years = int(years_match.group(1))
            if years >= 7:
                experience_level = "Senior"
            elif years >= 3:
                experience_level = "Mid"
            else:
                experience_level = "Junior"
        elif any(word in text_lower for word in ["senior", "lead", "principal", "director", "head of"]):
            experience_level = "Senior"
        elif any(word in text_lower for word in ["junior", "intern", "entry level", "fresher", "graduate"]):
            experience_level = "Junior"
        
        return {
            "text_length": len(text),
            "found_skills": all_skills,
            "detected_role": detected_role,
            "experience_level": experience_level
        }
