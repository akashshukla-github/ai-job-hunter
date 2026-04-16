from __future__ import annotations

from typing import Any


TERM_NORMALIZATION = {
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "sql": "SQL",
    "python": "Python",
    "aws": "AWS",
    "gcp": "GCP",
    "power bi": "Power BI",
    "scikit-learn": "scikit-learn",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "business intelligence": "Business Intelligence",
    "model deployment": "Model Deployment",
    "computer vision": "Computer Vision",
    "statistics": "Statistics",
    "excel": "Excel",
    "tableau": "Tableau",
    "numpy": "NumPy",
    "pandas": "pandas",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
}


def _normalize_term(term: str) -> str:
    cleaned = term.strip()
    if not cleaned:
        return ""

    lowered = cleaned.lower()
    if lowered in TERM_NORMALIZATION:
        return TERM_NORMALIZATION[lowered]

    return " ".join(word.capitalize() for word in cleaned.split())


def _clean_list(values: list[str]) -> list[str]:
    normalized_values = [_normalize_term(value) for value in values if value.strip()]
    seen: set[str] = set()
    result: list[str] = []

    for value in normalized_values:
        lowered = value.lower()
        if lowered not in seen:
            seen.add(lowered)
            result.append(value)

    return result


def _format_skills(skills: list[str], limit: int = 4) -> str:
    cleaned_skills = _clean_list(skills)
    if not cleaned_skills:
        return "Python and problem-solving"

    selected = cleaned_skills[:limit]
    if len(selected) == 1:
        return selected[0]
    if len(selected) == 2:
        return f"{selected[0]} and {selected[1]}"
    return f"{', '.join(selected[:-1])}, and {selected[-1]}"


def _profile_intro(profile: dict[str, Any]) -> str:
    roles = _clean_list(profile.get("preferred_roles", []))
    skills = _clean_list(profile.get("skills", []))

    role_text = roles[0] if roles else "Data-focused"
    skill_text = _format_skills(skills)

    return (
        f"I am interested in opportunities aligned with {role_text} roles, "
        f"with a background in {skill_text}."
    )


def _job_context(job: dict[str, Any]) -> tuple[str, str, str]:
    title = job.get("title", "the role")
    company = job.get("company", "your company")
    link = job.get("link", "")
    return title, company, link


def _closing_paragraph() -> str:
    return (
        "I would be grateful for the opportunity to be considered for this position. "
        "If helpful, I would be happy to share additional details about my projects and experience."
    )


def generate_application_email(job: dict[str, Any], profile: dict[str, Any]) -> dict[str, str]:
    title, company, link = _job_context(job)
    skills = job.get("skills", []) or profile.get("skills", [])
    skill_text = _format_skills(skills)

    subject = f"Application for {title} at {company}"

    body = (
        f"Dear Hiring Team,\n\n"
        f"I hope you are doing well.\n\n"
        f"I am writing to express my interest in the {title} position at {company}. "
        f"{_profile_intro(profile)}\n\n"
        f"My experience and interests align well with the role, especially in areas such as {skill_text}. "
        f"I am excited about the opportunity to contribute, learn, and grow in a strong team environment.\n\n"
        f"{_closing_paragraph()}\n\n"
        f"Job Link: {link or 'N/A'}\n\n"
        f"Best regards,\n"
        f"[Your Name]"
    )

    return {
        "subject": subject,
        "body": body,
    }


def generate_followup_email(job: dict[str, Any], profile: dict[str, Any]) -> dict[str, str]:
    title, company, link = _job_context(job)

    subject = f"Follow-up on {title} application - {company}"

    body = (
        f"Dear Hiring Team,\n\n"
        f"I hope you are doing well.\n\n"
        f"I wanted to follow up regarding my application for the {title} role at {company}. "
        f"I remain very interested in the opportunity and believe my background is a strong fit for the position.\n\n"
        f"{_profile_intro(profile)} "
        f"I would appreciate any update you may be able to share regarding the next steps in the process.\n\n"
        f"Job Link: {link or 'N/A'}\n\n"
        f"Thank you for your time and consideration.\n\n"
        f"Best regards,\n"
        f"[Your Name]"
    )

    return {
        "subject": subject,
        "body": body,
    }


def print_email_draft(email_draft: dict[str, str]) -> None:
    print("Email Draft")
    print("-----------")
    print(f"Subject: {email_draft.get('subject', 'N/A')}\n")
    print(email_draft.get("body", ""))


if __name__ == "__main__":
    sample_job = {
        "title": "Machine Learning Intern",
        "company": "Example AI Labs",
        "skills": ["Python", "Machine Learning", "Deep Learning"],
        "link": "https://example.com/job",
    }

    sample_profile = {
        "skills": ["ml", "ai", "sql"],
        "preferred_roles": ["ml engineer", "data science intern"],
    }

    print_email_draft(generate_application_email(sample_job, sample_profile))
    print()
    print_email_draft(generate_followup_email(sample_job, sample_profile))
