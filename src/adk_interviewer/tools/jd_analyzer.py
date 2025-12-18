"""
Job Description Analyzer Tool for ADK Interviewer.

Extracts key requirements and focus areas from job descriptions
to tailor interview questions appropriately.
"""

from typing import Optional
import re


def analyze_job_description(jd_text: str) -> dict:
    """
    Analyze a job description to extract key requirements.
    
    Identifies:
    - Required skills and technologies
    - Seniority level expected
    - Key responsibilities
    - Industry focus
    - Interview focus areas
    
    Args:
        jd_text: The job description text
        
    Returns:
        dict: {
            "role_title": str,             # Inferred role title
            "seniority": str,              # Expected seniority level
            "required_skills": list[str],  # Must-have skills
            "preferred_skills": list[str], # Nice-to-have skills
            "focus_areas": list[str],      # Key areas to test
            "industry": str,               # Industry context
            "summary": str                 # Brief JD summary
        }
        
    Example:
        >>> result = analyze_job_description("Senior Python Developer...")
        >>> print(result["required_skills"])  # ["Python", "Django", ...]
    """
    text_lower = jd_text.lower()
    
    # Skill categories for matching
    skill_patterns = {
        "Python": ["python", "django", "flask", "fastapi"],
        "JavaScript": ["javascript", "react", "vue", "angular", "node.js"],
        "Cloud": ["aws", "gcp", "azure", "cloud"],
        "DevOps": ["kubernetes", "docker", "ci/cd", "jenkins", "terraform"],
        "Data": ["sql", "postgresql", "mongodb", "redis", "elasticsearch"],
        "ML/AI": ["machine learning", "tensorflow", "pytorch", "nlp", "ai"],
        "System Design": ["microservices", "distributed", "scalable", "architecture"],
        "Security": ["security", "authentication", "encryption", "oauth"]
    }
    
    # Extract required skills
    required_skills = []
    preferred_skills = []
    
    # Check for "required" vs "preferred" sections
    required_section = ""
    preferred_section = ""
    
    if "required" in text_lower or "must have" in text_lower:
        required_match = re.search(
            r'(?:required|must have|requirements?)[:\s]*([^.]+(?:\.[^.]+){0,5})',
            text_lower
        )
        if required_match:
            required_section = required_match.group(1)
    
    if "preferred" in text_lower or "nice to have" in text_lower:
        preferred_match = re.search(
            r'(?:preferred|nice to have|bonus)[:\s]*([^.]+(?:\.[^.]+){0,5})',
            text_lower
        )
        if preferred_match:
            preferred_section = preferred_match.group(1)
    
    # Match skills to categories
    for category, keywords in skill_patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Determine if required or preferred
                if keyword in required_section or keyword not in preferred_section:
                    if category not in required_skills:
                        required_skills.append(category)
                else:
                    if category not in preferred_skills:
                        preferred_skills.append(category)
                break
    
    # Determine seniority
    seniority_patterns = {
        "Principal/Staff": ["principal", "staff", "distinguished", "fellow"],
        "Senior": ["senior", "sr.", "lead", "architect", "10+ years"],
        "Mid-Level": ["mid-level", "mid level", "3-5 years", "5+ years"],
        "Junior": ["junior", "jr.", "entry", "graduate", "0-2 years"]
    }
    
    seniority = "Mid-Level"  # Default
    for level, patterns in seniority_patterns.items():
        if any(p in text_lower for p in patterns):
            seniority = level
            break
    
    # Infer role title
    role_patterns = [
        r'(senior\s+)?(\w+\s+)?(developer|engineer|architect|manager)',
        r'(lead\s+)?(\w+\s+)?(developer|engineer)',
        r'(\w+\s+)(specialist|analyst|consultant)'
    ]
    
    role_title = "Software Engineer"  # Default
    for pattern in role_patterns:
        match = re.search(pattern, text_lower)
        if match:
            role_title = match.group(0).title()
            break
    
    # Identify industry
    industry_keywords = {
        "FinTech": ["fintech", "banking", "payments", "trading", "financial"],
        "HealthTech": ["healthcare", "medical", "clinical", "patient", "hipaa"],
        "E-commerce": ["ecommerce", "e-commerce", "retail", "shopping", "marketplace"],
        "SaaS": ["saas", "subscription", "b2b", "platform"],
        "Gaming": ["gaming", "game", "entertainment"],
        "AI/ML": ["artificial intelligence", "machine learning", "data science"]
    }
    
    industry = "Technology"  # Default
    for ind, keywords in industry_keywords.items():
        if any(k in text_lower for k in keywords):
            industry = ind
            break
    
    # Determine focus areas for interview
    focus_areas = required_skills[:3] if required_skills else ["General Software Engineering"]
    if "system design" in text_lower or "architecture" in text_lower:
        focus_areas.append("System Design")
    if "leadership" in text_lower or "mentor" in text_lower:
        focus_areas.append("Leadership & Communication")
    
    # Generate summary
    summary = (
        f"{seniority} {role_title} role in {industry}. "
        f"Key skills: {', '.join(required_skills[:4]) if required_skills else 'Not specified'}. "
        f"Interview should focus on: {', '.join(focus_areas[:3])}."
    )
    
    return {
        "role_title": role_title,
        "seniority": seniority,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "focus_areas": focus_areas[:5],
        "industry": industry,
        "summary": summary
    }
