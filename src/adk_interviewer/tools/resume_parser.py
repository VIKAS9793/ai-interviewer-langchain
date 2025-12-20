"""
Resume Parser Tool for ADK Interviewer.

Extracts relevant information from resume text or uploaded files.
Supports PDF, DOCX, and plain text formats via ADK artifacts.
"""

from typing import Optional, Any
import re
import logging

# Configure module logger
logger = logging.getLogger(__name__)


def parse_resume(resume_text: str, tool_context: Any) -> dict:
    """
    Parse resume text or uploaded file to extract relevant information.
    
    Analyzes the resume to identify:
    - Technical skills
    - Years of experience
    - Education background
    - Notable projects
    - Key technologies
    
    Args:
        resume_text: Plain text content of the resume (or empty if using artifact)
        tool_context: ADK tool execution context for accessing uploaded files
        
    Returns:
        dict: {
            "skills": list[str],           # Identified technical skills
            "experience_years": int,       # Estimated years of experience
            "education": str,              # Highest education level
            "technologies": list[str],     # Specific technologies mentioned
            "projects": list[str],         # Notable projects
            "seniority": str,              # Estimated seniority level
            "summary": str                 # Brief candidate summary
        }
        
    Example:
        >>> result = parse_resume("5 years Python developer...", tool_context)
        >>> print(result["skills"])  # ["Python", "Django", ...]
    """
    # Try to load from uploaded file artifact first
    final_text = resume_text
    
    if tool_context and hasattr(tool_context, 'artifacts'):
        artifacts = tool_context.artifacts or []
        if artifacts:
            # User uploaded a file - extract text from artifact
            try:
                artifact = artifacts[0]  # First uploaded file
                
                # Check MIME type to determine parsing strategy
                mime_type = getattr(artifact, 'mime_type', 'text/plain')
                
                if 'pdf' in mime_type.lower():
                    final_text = _extract_text_from_pdf_artifact(artifact)
                elif 'word' in mime_type.lower() or 'officedocument' in mime_type.lower():
                    final_text = _extract_text_from_docx_artifact(artifact)
                else:
                    # Plain text or unknown - try as-is
                    final_text = getattr(artifact, 'data', resume_text)
                    if isinstance(final_text, bytes):
                        final_text = final_text.decode('utf-8', errors='ignore')
                        
            except Exception as e:
                # Fallback to provided text if artifact parsing fails
                logger.warning(f"Artifact parsing failed: {e}, using provided text")
                pass
    
    if not final_text or len(final_text.strip()) < 10:
        return {
            "skills": [],
            "experience_years": 0,
            "education": "Not specified",
            "technologies": [],
            "projects": [],
            "seniority": "Unknown",
            "summary": "No resume content provided"
        }
    
    text_lower = final_text.lower()
    
    # Skill extraction patterns
    programming_languages = [
        "python", "javascript", "typescript", "java", "c++", "c#",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala"
    ]
    
    frameworks = [
        "react", "angular", "vue", "django", "flask", "fastapi",
        "spring", "express", "next.js", "node.js", "tensorflow",
        "pytorch", "kubernetes", "docker", "aws", "gcp", "azure"
    ]
    
    databases = [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "oracle", "sql server"
    ]
    
    # Extract skills
    found_skills = []
    for lang in programming_languages:
        if lang in text_lower:
            found_skills.append(lang.capitalize())
    
    for fw in frameworks:
        if fw in text_lower:
            found_skills.append(fw.title())
    
    for db in databases:
        if db in text_lower:
            found_skills.append(db.title())
    
    # Extract years of experience
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience[:\s]*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*exp'
    ]
    
    experience_years = 0
    for pattern in experience_patterns:
        match = re.search(pattern, text_lower)
        if match:
            experience_years = int(match.group(1))
            break
    
    # Estimate from dates if not explicit
    if experience_years == 0:
        year_mentions = re.findall(r'20[0-2]\d', final_text)
        if year_mentions:
            earliest = min(int(y) for y in year_mentions)
            experience_years = max(0, 2025 - earliest)
    
    # Extract education
    education = "Not specified"
    education_keywords = {
        "phd": "PhD",
        "ph.d": "PhD",
        "doctorate": "PhD",
        "master": "Master's Degree",
        "msc": "Master's Degree",
        "mba": "MBA",
        "bachelor": "Bachelor's Degree",
        "bsc": "Bachelor's Degree",
        "b.tech": "Bachelor's Degree",
        "b.e.": "Bachelor's Degree"
    }
    
    for keyword, level in education_keywords.items():
        if keyword in text_lower:
            education = level
            break
    
    # Determine seniority
    if experience_years >= 10:
        seniority = "Principal/Staff"
    elif experience_years >= 7:
        seniority = "Senior"
    elif experience_years >= 4:
        seniority = "Mid-Level"
    elif experience_years >= 1:
        seniority = "Junior"
    else:
        seniority = "Entry-Level"
    
    # Extract project mentions (simple heuristic)
    projects = []
    project_patterns = [
        r'(?:built|developed|created|led|architected)\s+(?:a\s+)?([^.]+)',
        r'project[:\s]+([^.]+)'
    ]
    
    for pattern in project_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches[:3]:  # Limit to 3 projects
            if len(match) > 10 and len(match) < 100:
                projects.append(match.strip().capitalize())
    
    # Generate summary
    skill_summary = ", ".join(found_skills[:5]) if found_skills else "various technologies"
    summary = (
        f"{seniority} candidate with {experience_years} years of experience. "
        f"Skilled in {skill_summary}. {education}."
    )
    
    return {
        "skills": found_skills[:10],  # Top 10 skills
        "experience_years": experience_years,
        "education": education,
        "technologies": found_skills[:5],  # Top 5 as technologies
        "projects": projects[:3],
        "seniority": seniority,
        "summary": summary
    }


def _extract_text_from_pdf_artifact(artifact) -> str:
    """
    Extract text from PDF artifact.
    
    Uses PyPDF2 if available, otherwise returns raw data as text.
    """
    try:
        import PyPDF2
        import io
        
        # Get binary data from artifact
        pdf_data = artifact.data if hasattr(artifact, 'data') else b''
        if isinstance(pdf_data, str):
            pdf_data = pdf_data.encode('utf-8')
        
        # Parse PDF
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except ImportError:
        # PyPDF2 not installed - fallback to raw text
        logger.warning("PyPDF2 not installed, using raw text extraction")
        data = artifact.data if hasattr(artifact, 'data') else b''
        if isinstance(data, bytes):
            return data.decode('utf-8', errors='ignore')
        return str(data)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""


def _extract_text_from_docx_artifact(artifact) -> str:
    """
    Extract text from DOCX artifact.
    
    Uses python-docx if available, otherwise returns raw data as text.
    """
    try:
        import docx
        import io
        
        # Get binary data from artifact
        docx_data = artifact.data if hasattr(artifact, 'data') else b''
        if isinstance(docx_data, str):
            docx_data = docx_data.encode('utf-8')
        
        # Parse DOCX
        doc_file = io.BytesIO(docx_data)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
        
    except ImportError:
        # python-docx not installed - fallback to raw text
        logger.warning("python-docx not installed, using raw text extraction")
        data = artifact.data if hasattr(artifact, 'data') else b''
        if isinstance(data, bytes):
            return data.decode('utf-8', errors='ignore')
        return str(data)
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return ""
