"""
Job Description Parser Module

Extracts role title, company name, and requirements from job descriptions.
Supports parsing from:
- Job URLs (Google Careers, LinkedIn, Lever, Greenhouse, etc.)
- Pasted JD text

From AI_RESEARCH_FINDINGS.md:
- Agent retrieves context from JD
- Generates role-specific questions using retrieved context
"""
import re
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class JDParser:
    """
    Job Description Parser for extracting role information.
    
    Supports:
    - URL parsing (Google Careers, LinkedIn, etc.)
    - Text parsing (pasted JD content)
    - Role title extraction
    - Requirements extraction
    """
    
    # Common job board patterns
    URL_PATTERNS = {
        "google": r"google\.com.*careers.*\/(\d+)-(.+?)(?:\?|$)",
        "linkedin": r"linkedin\.com.*jobs.*view\/(\d+)",
        "lever": r"lever\.co\/(.+?)\/(.+?)(?:\?|$)",
        "greenhouse": r"boards\.greenhouse\.io\/(.+?)\/jobs\/(\d+)",
    }
    
    # Role title keywords to detect from text
    ROLE_KEYWORDS = {
        "product manager": "Product Manager",
        "product management": "Product Manager",
        "software engineer": "Software Engineer",
        "software developer": "Software Developer",
        "backend engineer": "Backend Engineer",
        "frontend engineer": "Frontend Engineer",
        "full stack": "Full Stack Engineer",
        "data scientist": "Data Scientist",
        "data engineer": "Data Engineer",
        "machine learning": "Machine Learning Engineer",
        "ml engineer": "Machine Learning Engineer",
        "devops": "DevOps Engineer",
        "sre": "Site Reliability Engineer",
        "site reliability": "Site Reliability Engineer",
        "cloud engineer": "Cloud Engineer",
        "security engineer": "Security Engineer",
        "qa engineer": "QA Engineer",
        "test engineer": "Test Engineer",
        "mobile developer": "Mobile Developer",
        "ios developer": "iOS Developer",
        "android developer": "Android Developer",
        "solutions architect": "Solutions Architect",
        "technical program manager": "Technical Program Manager",
        "tpm": "Technical Program Manager",
        "engineering manager": "Engineering Manager",
    }
    
    # Company name detection patterns
    COMPANY_PATTERNS = [
        r"(?:at|@)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
        r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+is\s+(?:hiring|looking|seeking)",
        r"^([A-Z][a-zA-Z]+)\s*[-–—]\s*",
    ]
    
    @classmethod
    def parse_url(cls, url: str) -> Dict[str, Any]:
        """
        Extract role information from job URL.
        
        Args:
            url: Job posting URL (Google Careers, LinkedIn, etc.)
            
        Returns:
            Dict with role_title, company_name, url_id
        """
        if not url or not url.strip():
            return {"role_title": None, "company_name": None, "source": "empty"}
        
        url = url.strip().lower()
        parsed = urlparse(url)
        
        result = {
            "role_title": None,
            "company_name": None,
            "url_id": None,
            "source": "url"
        }
        
        # Detect Google Careers
        if "google.com" in parsed.netloc and "careers" in url:
            result["company_name"] = "Google"
            # Extract role from URL path
            # Example: /product-manager-youtube-channel-memberships
            path_parts = parsed.path.split("/")
            for part in path_parts:
                if "-" in part and len(part) > 10:
                    # Convert slug to title
                    role_words = part.split("-")
                    # Remove job ID if present
                    if role_words and role_words[0].isdigit():
                        role_words = role_words[1:]
                    role_title = " ".join(word.capitalize() for word in role_words if not word.isdigit())
                    if role_title:
                        result["role_title"] = cls._clean_role_title(role_title)
                        break
        
        # Detect LinkedIn
        elif "linkedin.com" in parsed.netloc:
            result["source"] = "linkedin"
            # LinkedIn requires scraping for title, URL doesn't contain it
            
        # Detect Lever
        elif "lever.co" in parsed.netloc:
            match = re.search(r"lever\.co/([^/]+)/([^/?]+)", url)
            if match:
                result["company_name"] = match.group(1).replace("-", " ").title()
                result["role_title"] = match.group(2).replace("-", " ").title()
        
        # Detect Greenhouse
        elif "greenhouse.io" in parsed.netloc:
            match = re.search(r"boards\.greenhouse\.io/([^/]+)", url)
            if match:
                result["company_name"] = match.group(1).replace("_", " ").title()
        
        logger.info(f"🔎 Parsed URL: {result}")
        return result
    
    @classmethod
    def parse_text(cls, jd_text: str) -> Dict[str, Any]:
        """
        Extract role information from JD text.
        
        Args:
            jd_text: Job description text (pasted or scraped)
            
        Returns:
            Dict with role_title, company_name, requirements
        """
        if not jd_text or len(jd_text.strip()) < 20:
            return {"role_title": None, "company_name": None, "requirements": [], "source": "empty"}
        
        text = jd_text.strip()
        text_lower = text.lower()
        
        result = {
            "role_title": None,
            "company_name": None,
            "requirements": [],
            "responsibilities": [],
            "source": "text"
        }
        
        # Extract role title
        for keyword, role in cls.ROLE_KEYWORDS.items():
            if keyword in text_lower:
                result["role_title"] = role
                break
        
        # Try to get more specific title from first lines
        first_lines = text.split("\n")[:5]
        for line in first_lines:
            line = line.strip()
            # Look for lines that look like job titles
            if 10 < len(line) < 100 and not line.startswith("About"):
                for keyword, role in cls.ROLE_KEYWORDS.items():
                    if keyword in line.lower():
                        # Use the actual line as title (more specific)
                        result["role_title"] = cls._clean_role_title(line)
                        break
                if result["role_title"]:
                    break
        
        # Extract company name
        for pattern in cls.COMPANY_PATTERNS:
            match = re.search(pattern, text)
            if match:
                result["company_name"] = match.group(1).strip()
                break
        
        # Extract requirements
        result["requirements"] = cls._extract_requirements(text)
        
        logger.info(f"🔎 Parsed JD text: role={result['role_title']}, company={result['company_name']}")
        return result
    
    @classmethod
    def parse(cls, url: Optional[str] = None, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse job description from URL and/or text.
        Combines both sources for best results.
        
        Args:
            url: Job posting URL (optional)
            text: Job description text (optional)
            
        Returns:
            Dict with role_title, company_name, requirements
        """
        result = {
            "role_title": None,
            "company_name": None,
            "requirements": [],
            "source": "combined"
        }
        
        # Parse URL first
        if url:
            url_result = cls.parse_url(url)
            result["role_title"] = url_result.get("role_title")
            result["company_name"] = url_result.get("company_name")
        
        # Parse text to fill gaps and add requirements
        if text:
            text_result = cls.parse_text(text)
            if not result["role_title"]:
                result["role_title"] = text_result.get("role_title")
            if not result["company_name"]:
                result["company_name"] = text_result.get("company_name")
            result["requirements"] = text_result.get("requirements", [])
        
        # Clean up role title
        if result["role_title"]:
            result["role_title"] = cls._clean_role_title(result["role_title"])
        
        return result
    
    @classmethod
    def _clean_role_title(cls, title: str) -> str:
        """Clean and normalize role title."""
        if not title:
            return ""
        
        # Remove common suffixes
        title = re.sub(r"\s*[-–—]\s*\d+.*$", "", title)  # Remove "- 12345" IDs
        title = re.sub(r"\s*\(.*\)$", "", title)  # Remove "(Remote)"
        title = re.sub(r"\s*,.*$", "", title)  # Remove ", San Francisco"
        
        # Capitalize properly
        title = " ".join(word.capitalize() if word.lower() not in ["and", "or", "the", "of"] else word 
                        for word in title.split())
        
        # Truncate if too long
        if len(title) > 60:
            title = title[:60].rsplit(" ", 1)[0]
        
        return title.strip()
    
    @classmethod
    def _extract_requirements(cls, text: str) -> List[str]:
        """Extract requirements from JD text."""
        requirements = []
        
        # Look for requirements section
        patterns = [
            r"(?:requirements?|qualifications?|must have|you have)[:\s]*\n((?:[-•*]\s*.+\n?)+)",
            r"(?:we're looking for|ideal candidate)[:\s]*\n((?:[-•*]\s*.+\n?)+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                section = match.group(1)
                items = re.findall(r"[-•*]\s*(.+)", section)
                requirements.extend([item.strip() for item in items[:5]])
                break
        
        # Fallback: extract key skills mentioned
        if not requirements:
            skill_patterns = [
                r"(\d+)\+?\s*years?\s*(?:of\s+)?(.+?)(?:experience|required)",
                r"experience\s+(?:with|in)\s+(.+?)(?:\.|,|and)",
            ]
            for pattern in skill_patterns:
                matches = re.findall(pattern, text.lower())
                for match in matches[:5]:
                    if isinstance(match, tuple):
                        requirements.append(f"{match[0]}+ years {match[1].strip()}")
                    else:
                        requirements.append(match.strip())
        
        return requirements[:5]  # Limit to 5


# Convenience function
def parse_job_description(url: Optional[str] = None, text: Optional[str] = None) -> Dict[str, Any]:
    """Parse job description from URL and/or text."""
    return JDParser.parse(url=url, text=text)
