from __future__ import annotations

import re
from typing import Any


KEYWORD_EXPANSIONS = {
    "ml": [
        "machine learning",
        "deep learning",
        "nlp",
        "computer vision",
        "data science",
    ],
    "ai": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "nlp",
        "data science",
    ],
    "data": [
        "data science",
        "data analytics",
        "analytics",
        "analysis",
        "data analysis",
        "sql",
        "python",
    ],
    "python": ["pandas", "numpy", "scikit-learn", "automation"],
    "analytics": ["analysis", "data analysis", "business intelligence"],
}

ROLE_FAMILIES = {
    "ml": [
        "machine learning engineer",
        "machine learning intern",
        "ml engineer",
        "ai engineer",
        "data scientist",
        "data science intern",
    ],
    "ai": [
        "artificial intelligence engineer",
        "ai engineer",
        "machine learning engineer",
        "machine learning intern",
        "data scientist",
        "data science intern",
    ],
    "data science": [
        "data science intern",
        "data scientist",
        "data analyst",
        "analytics intern",
        "business analyst",
        "machine learning intern",
    ],
    "data analyst": [
        "data analyst",
        "business analyst",
        "analytics intern",
        "data science intern",
    ],
    "python developer": [
        "python developer",
        "backend developer",
        "software developer",
        "automation intern",
        "data science intern",
    ],
}

TITLE_INFERENCES = {
    "data science": ["python", "machine learning", "statistics", "data analysis"],
    "data scientist": ["python", "machine learning", "statistics"],
    "data analyst": ["sql", "excel", "tableau", "data analysis"],
    "analytics": ["sql", "excel", "data analysis", "business intelligence"],
    "machine learning": ["python", "machine learning", "deep learning", "model deployment"],
    "ml engineer": ["python", "machine learning", "deep learning", "model deployment"],
    "ai engineer": ["python", "artificial intelligence", "machine learning", "deep learning"],
    "nlp": ["python", "nlp", "machine learning"],
    "computer vision": ["python", "computer vision", "deep learning"],
    "business analyst": ["analysis", "sql", "excel"],
    "python developer": ["python"],
}

REMOTE_KEYWORDS = {"remote", "work from home", "wfh", "hybrid", "anywhere"}
TOKEN_SPLIT_PATTERN = re.compile(r"[^a-z0-9\+\#]+")


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    return re.sub(r"\s+", " ", text)


def _tokenize(value: str) -> set[str]:
    normalized = _normalize_text(value)
    if not normalized:
        return set()
    return {token for token in TOKEN_SPLIT_PATTERN.split(normalized) if token}


def _expand_term(term: str) -> set[str]:
    normalized = _normalize_text(term)
    if not normalized:
        return set()

    expanded = {normalized}

    for alias, synonyms in KEYWORD_EXPANSIONS.items():
        normalized_synonyms = {_normalize_text(synonym) for synonym in synonyms}
        if normalized == alias or normalized in normalized_synonyms:
            expanded.add(alias)
            expanded.update(normalized_synonyms)

    for family, related_roles in ROLE_FAMILIES.items():
        normalized_roles = {_normalize_text(role) for role in related_roles}
        if normalized == family or normalized in normalized_roles:
            expanded.add(family)
            expanded.update(normalized_roles)

    return expanded


def _expand_terms(terms: list[str]) -> set[str]:
    expanded_terms: set[str] = set()
    for term in terms:
        expanded_terms.update(_expand_term(term))
    return expanded_terms


def infer_skills_from_title(title: str) -> list[str]:
    normalized_title = _normalize_text(title)
    inferred: list[str] = []
    seen: set[str] = set()

    for pattern, skills in TITLE_INFERENCES.items():
        if pattern in normalized_title:
            for skill in skills:
                normalized_skill = _normalize_text(skill)
                if normalized_skill and normalized_skill not in seen:
                    seen.add(normalized_skill)
                    inferred.append(skill)

    return inferred


def _extract_job_text(job: dict[str, Any]) -> tuple[str, str, list[str]]:
    title = _normalize_text(job.get("title"))
    skills = [
        _normalize_text(skill)
        for skill in job.get("skills", [])
        if _normalize_text(skill)
    ]

    if not skills:
        skills = [
            _normalize_text(skill)
            for skill in infer_skills_from_title(job.get("title", ""))
            if _normalize_text(skill)
        ]

    combined_text = " ".join(
        part
        for part in [
            title,
            " ".join(skills),
            _normalize_text(job.get("location")),
            _normalize_text(job.get("company")),
        ]
        if part
    )
    return title, combined_text, skills


def _match_terms_in_text(terms: set[str], text: str) -> set[str]:
    matches: set[str] = set()
    if not text:
        return matches

    tokens = _tokenize(text)
    for term in terms:
        if not term:
            continue
        if " " in term:
            if term in text:
                matches.add(term)
        elif term in tokens:
            matches.add(term)
    return matches


def _location_preference_mode(profile: dict[str, Any]) -> tuple[list[str], bool]:
    preferred_locations = [
        _normalize_text(location)
        for location in profile.get("locations", [])
        if _normalize_text(location)
    ]
    wants_remote = any(location in REMOTE_KEYWORDS for location in preferred_locations)
    return preferred_locations, wants_remote


def _match_locations(job: dict[str, Any], profile: dict[str, Any]) -> bool:
    preferred_locations, wants_remote = _location_preference_mode(profile)
    if not preferred_locations:
        return True

    job_location = _normalize_text(job.get("location"))
    if not job_location:
        return wants_remote

    if wants_remote and any(keyword in job_location for keyword in REMOTE_KEYWORDS):
        return True

    specific_locations = [location for location in preferred_locations if location not in REMOTE_KEYWORDS]
    if specific_locations:
        return any(location in job_location or job_location in location for location in specific_locations)

    return wants_remote


def _get_matches(job: dict[str, Any], profile: dict[str, Any]) -> tuple[set[str], set[str]]:
    title, combined_text, job_skills = _extract_job_text(job)
    skills_text = " ".join(job_skills)

    expanded_profile_skills = _expand_terms(profile.get("skills", []))
    expanded_profile_roles = _expand_terms(profile.get("preferred_roles", []))

    role_matches = _match_terms_in_text(expanded_profile_roles, title or combined_text)
    skill_matches = _match_terms_in_text(expanded_profile_skills, skills_text or combined_text)

    if not skill_matches:
        skill_matches = _match_terms_in_text(expanded_profile_skills, combined_text)

    if not role_matches:
        role_matches = _match_terms_in_text(expanded_profile_roles, combined_text)

    return role_matches, skill_matches


def is_relevant(job: dict[str, Any], profile: dict[str, Any]) -> bool:
    role_matches, skill_matches = _get_matches(job, profile)
    location_match = _match_locations(job, profile)
    combined_match_count = len(role_matches) + len(skill_matches)

    if location_match and combined_match_count >= 1:
        return True

    return combined_match_count >= 2


def score_job(job: dict[str, Any], profile: dict[str, Any]) -> int:
    role_matches, skill_matches = _get_matches(job, profile)
    location_match = _match_locations(job, profile)

    weighted_score = (len(skill_matches) * 2) + (len(role_matches) * 2)

    if len(skill_matches) >= 2:
        weighted_score += 1
    if len(role_matches) >= 2:
        weighted_score += 1
    if skill_matches and role_matches:
        weighted_score += 2
    if location_match and profile.get("locations"):
        weighted_score += 1

    return max(0, min(10, weighted_score))


def format_job(job: dict[str, Any]) -> dict[str, Any]:
    location = _normalize_text(job.get("location"))
    readable_location = job.get("location") or "N/A"
    job_type = "Remote" if any(keyword in location for keyword in REMOTE_KEYWORDS) else "On-site"
    skills = job.get("skills") or infer_skills_from_title(job.get("title", ""))
    source = _normalize_text(job.get("source")) or "unknown"

    return {
        "title": job.get("title") or "N/A",
        "company": job.get("company") or "N/A",
        "location": readable_location,
        "type": job_type,
        "skills": skills,
        "salary": job.get("salary") or "N/A",
        "link": job.get("link") or "N/A",
        "source": source.title(),
    }


def aggregate_jobs(
    all_jobs_list: list[dict[str, Any]],
    profile: dict[str, Any],
    limit: int = 20,
) -> list[dict[str, Any]]:
    ranked_jobs: list[dict[str, Any]] = []
    seen_links: set[str] = set()

    for job in all_jobs_list:
        if not isinstance(job, dict):
            continue

        link = _normalize_text(job.get("link"))
        if link and link in seen_links:
            continue

        if not is_relevant(job, profile):
            continue

        formatted_job = format_job(job)
        formatted_job["score"] = score_job(job, profile)
        ranked_jobs.append(formatted_job)

        if link:
            seen_links.add(link)

    ranked_jobs.sort(
        key=lambda item: (
            item["score"],
            item["type"] == "Remote",
            item["title"].lower(),
        ),
        reverse=True,
    )
    return ranked_jobs[:limit]


def print_jobs(jobs: list[dict[str, Any]]) -> None:
    for index, job in enumerate(jobs, start=1):
        print(f"{index}. {job['title']} - {job['company']}")
        print(f"   Location: {job['location']} ({job['type']})")
        print(f"   Skills: {', '.join(job['skills']) if job['skills'] else 'N/A'}")
        print(f"   Salary: {job['salary']}")
        print(f"   Source: {job['source']}")
        print(f"   Score: {job['score']}")
        print(f"   Link: {job['link']}")
        print()
