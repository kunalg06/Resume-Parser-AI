import re
from typing import List, Dict, Any

import spacy

# Load small English model (downloaded earlier)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d[\d\-\s]{7,}\d)"  # simple, not perfect


# Contact info (email, phone)
def extract_contact_info(text: str) -> Dict[str, str]:
    email_match = re.search(EMAIL_REGEX, text)
    phone_match = re.search(PHONE_REGEX, text)

    email = email_match.group(0) if email_match else ""
    phone = phone_match.group(0) if phone_match else ""

    return {
        "email": email.strip(),
        "phone": phone.strip(),
    }


# Name (using spaCy PERSON + fallback)
def extract_name(text: str) -> str:
    # Try spaCy first
    doc = nlp(text[:1000])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # Fallback: first line that doesn't look like contact info or a heading
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:5]:  # look at top few lines
        lower = line.lower()
        if looks_like_contact(line):
            continue
        if any(kw in lower for kw in ["summary", "profile", "experience", "education"]):
            continue
        # simple heuristic: 2–4 words
        if 1 < len(line.split()) <= 4:
            return line
    return ""


SUMMARY_KEYWORDS = ["summary", "profile", "about me", "professional summary"]
SECTION_STOP_WORDS = [
    "work experience",
    "experience",
    "work history",
    "employment",
    "projects",
    "education",
    "skills",
    "technical skills",
]


def looks_like_section_heading(line: str) -> bool:
    """
    Treat a line as a section heading if:
    - It is short (<= 5 words), and
    - It contains a known section word, and
    - It's mostly uppercase or title-case.
    """
    words = line.strip().split()
    if not words or len(words) > 5:
        return False

    lower = line.lower()
    if not any(stop in lower for stop in SECTION_STOP_WORDS):
        return False

    # crude heuristic: many resumes use uppercase headings
    if line.isupper():
        return True

    # or title-like, e.g. "Work Experience"
    if line.istitle():
        return True

    return False


def looks_like_contact(line: str) -> bool:
    """
    Return True if a line looks like contact info:
    - Contains an email
    - Contains 'linkedin' or 'github'
    - Contains a long number (likely phone)
    """
    lower = line.lower()

    # Email pattern
    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", line):
        return True

    # Common social/contact words
    if "linkedin" in lower or "github" in lower:
        return True

    # Many digits usually means phone
    digits = sum(ch.isdigit() for ch in line)
    if digits >= 6:
        return True

    return False


def extract_summary(text: str, max_lines: int = 5) -> str:
    """
    1) Find a line containing 'SUMMARY' / 'PROFILE' etc.
    2) Collect the next few lines until we hit a *heading* line
       like 'WORK EXPERIENCE' (detected by looks_like_section_heading).
    3) Skip contact-style lines (phone/email/links).
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""

    # Find SUMMARY heading line
    start_idx = None
    for i, line in enumerate(lines):
        lower = line.lower()
        if any(kw in lower for kw in SUMMARY_KEYWORDS):
            start_idx = i
            break

    if start_idx is None:
        return ""

    summary_lines = []
    # start from line AFTER the "SUMMARY" heading
    for line in lines[start_idx + 1 :]:
        # Stop if we hit another section heading (e.g. WORK EXPERIENCE)
        if looks_like_section_heading(line):
            break

        if looks_like_contact(line):
            continue

        summary_lines.append(line)
        if len(summary_lines) >= max_lines:
            break

    return " ".join(summary_lines)


# Education / experience sections
EDU_KEYWORDS = ["education", "academic background", "qualifications"]
EXP_KEYWORDS = ["experience", "work history", "employment", "professional experience"]


def extract_section(text: str, keywords: List[str], max_lines: int = 15) -> List[str]:
    """
    Very simple section extractor:
    - Convert text to lines
    - Find a line containing any keyword
    - Take that line + next max_lines lines
    """
    lines = text.splitlines()
    lower_lines = [l.lower() for l in lines]

    for idx, lower_line in enumerate(lower_lines):
        if any(kw in lower_line for kw in keywords):
            start = idx
            end = min(len(lines), idx + max_lines)
            return [lines[i].strip() for i in range(start, end) if lines[i].strip()]

    return []


def extract_education(text: str) -> List[str]:
    return extract_section(text, EDU_KEYWORDS)


def extract_experience(text: str, max_lines: int = 50) -> List[str]:
    """
    1) Find a heading line containing 'WORK EXPERIENCE' (prefer),
       or other experience keywords as a fallback.
    2) Take lines after that until the next section heading.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return []

    # Prefer a heading with "WORK EXPERIENCE"
    start_idx = None
    for i, line in enumerate(lines):
        lower = line.lower()
        if "work experience" in lower and looks_like_section_heading(line):
            start_idx = i
            break

    # If not found, fall back to any heading line with experience keywords
    if start_idx is None:
        for i, line in enumerate(lines):
            lower = line.lower()
            if any(kw in lower for kw in EXP_KEYWORDS) and looks_like_section_heading(line):
                start_idx = i
                break

    if start_idx is None:
        return []

    experience_lines = []
    for line in lines[start_idx + 1 :]:
        # Stop at next section heading (e.g. EDUCATION, SKILLS)
        if looks_like_section_heading(line):
            break
        experience_lines.append(line)
        if len(experience_lines) >= max_lines:
            break

    return experience_lines


# Skills (simple list matching)
SKILL_LIST = [
    "python", "java", "c++", "sql", "mysql", "postgresql",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "aws", "azure", "gcp", "docker", "kubernetes",
    "machine learning", "deep learning", "nlp",
]


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()

    for skill in SKILL_LIST:
        if skill.lower() in text_lower:
            found.add(skill)

    return sorted(found)


# Roles (very simple heuristic)
ROLE_KEYWORDS = [
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "software engineer",
    "backend developer",
    "frontend developer",
    "full stack developer",
    "devops engineer",
]


def extract_roles(text: str) -> List[str]:
    text_lower = text.lower()
    roles = []
    for role in ROLE_KEYWORDS:
        if role in text_lower:
            roles.append(role.title())
    return roles


# Main parse function
def parse_resume(text: str) -> Dict[str, Any]:
    contact = extract_contact_info(text)
    name = extract_name(text)
    education = extract_education(text)
    experience = extract_experience(text)
    skills = extract_skills(text)
    roles = extract_roles(text)
    summary = extract_summary(text)

    return {
        "name": name,
        "email": contact["email"],
        "phone": contact["phone"],
        "summary": summary,
        "roles": roles,
        "skills": skills,
        "education": education,
        "experience": experience,
    }
