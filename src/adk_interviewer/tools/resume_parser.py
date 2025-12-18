"""
Resume Parser Tool for ADK Interviewer.

Extracts relevant information from resume text for
contextualized interview question generation.
"""

from typing import Optional
import re


def parse_resume(resume_text: str) -> dict:
    """
    Parse resume text to extract relevant information.
    
    Analyzes the resume to identify:
    - Technical skills
    - Years of experience
    - Education background
    - Notable projects
    - Key technologies
    
    Args:
        resume_text: Plain text content of the resume
        
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
        >>> result = parse_resume("5 years Python developer...")
        >>> print(result["skills"])  # ["Python", "Django", ...]
    """
    text_lower = resume_text.lower()
    
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
        year_mentions = re.findall(r'20[0-2]\d', resume_text)
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
