from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any


KEYWORD_EXPANSIONS = {
    "ml": ["machine learning", "deep learning", "nlp", "computer vision"],
    "ai": ["artificial intelligence", "machine learning", "deep learning", "nlp"],
    "data": ["data science", "analytics", "data analysis", "sql", "python"],
}

SKILL_KEYWORDS = [
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "statistics",
    "nlp",
    "natural language processing",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "spark",
    "hadoop",
    "aws",
    "azure",
    "gcp",
    "docker",
    "git",
    "model deployment",
    "feature engineering",
    "data visualization",
    "business intelligence",
]

ROLE_KEYWORDS = [
    "data science intern",
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "business analyst",
    "research intern",
    "python developer",
]

TITLE_INFERENCES = {
    "data science": ["python", "machine learning", "statistics", "data analysis"],
    "data scientist": ["python", "machine learning", "statistics"],
    "data analyst": ["sql", "excel", "tableau", "data analysis"],
    "machine learning": ["python", "machine learning", "model deployment"],
    "ai engineer": ["python", "artificial intelligence", "machine learning"],
    "business analyst": ["sql", "excel", "business intelligence"],
}

BUZZWORDS = {
    "hardworking": "Replace with a measurable achievement.",
    "passionate": "Replace with evidence of domain experience.",
    "team player": "Show collaboration through a project or result.",
    "go-getter": "Replace with specific initiative or ownership.",
    "self-starter": "Show independent work through a concrete example.",
    "dynamic": "Use a stronger action verb tied to outcomes.",
    "motivated": "Show motivation through impact, not adjectives.",
    "results-driven": "State the actual result with numbers.",
    "detail-oriented": "Mention quality or accuracy improvements instead.",
    "excellent communication skills": "Replace with a real presentation, report, or cross-team example.",
    "responsible for": "Use a stronger verb like built, analyzed, automated, or improved.",
    "worked on": "Replace with a specific ownership verb.",
    "helped with": "Clarify what you actually did.",
    "various": "Name the exact tools or tasks.",
    "etc": "List the most relevant items explicitly.",
}

WEAK_PHRASE_REPLACEMENTS = {
    "worked on": "built",
    "helped with": "supported",
    "responsible for": "managed",
}

ACTION_VERBS = [
    "built",
    "analyzed",
    "developed",
    "automated",
    "optimized",
    "designed",
    "implemented",
    "improved",
    "evaluated",
    "deployed",
    "created",
    "delivered",
    "engineered",
]

GENERIC_SKILLS = {
    "analysis",
    "analytics",
}

TOKEN_SPLIT_PATTERN = re.compile(r"[^a-z0-9\+\#]+")
BULLET_PREFIX_PATTERN = re.compile(r"^\s*[-*•]\s*")
SOFT_SKILL_PATTERNS = [
    "team player",
    "excellent communication skills",
    "good communication",
    "leadership",
    "hardworking",
    "passionate",
    "self-starter",
    "motivated",
]

STRICT_LITERAL_SKILLS = {
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "statistics",
    "nlp",
    "natural language processing",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "spark",
    "hadoop",
    "aws",
    "azure",
    "gcp",
    "docker",
    "git",
    "model deployment",
    "feature engineering",
    "data visualization",
    "business intelligence",
}



def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _tokenize(text: str) -> set[str]:
    normalized = _normalize_text(text)
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
    return expanded


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = _normalize_text(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(item)
    return result


def _looks_like_bullet(line: str) -> bool:
    stripped = line.strip()
    if BULLET_PREFIX_PATTERN.match(line):
        return True
    return len(stripped.split()) <= 20


def _clean_line_for_rewrite(line: str) -> str:
    cleaned = BULLET_PREFIX_PATTERN.sub("", line).strip()
    normalized = _normalize_text(cleaned)

    for buzzword in BUZZWORDS:
        normalized = re.sub(rf"\b{re.escape(buzzword)}\b", "", normalized)

    for weak_phrase, replacement in WEAK_PHRASE_REPLACEMENTS.items():
        if normalized.startswith(weak_phrase):
            normalized = normalized.replace(weak_phrase, replacement, 1)

    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip(" ,.-")
    return normalized


def _choose_missing_keywords(missing_keywords: list[str], limit: int = 2) -> list[str]:
    selected = []
    for keyword in missing_keywords:
        normalized = _normalize_text(keyword)
        if normalized and normalized not in GENERIC_SKILLS:
            selected.append(keyword)
        if len(selected) == limit:
            break
    return selected


def _ensure_action_start(text: str) -> str:
    if not text:
        return "Built machine learning project with measurable impact"

    if any(text.startswith(verb) for verb in ACTION_VERBS):
        return text

    if text.startswith(("aspiring", "fresher", "student")):
        return f"Built projects as an {text}"

    return f"Built {text}"


def _capitalize_sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def load_resume_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Only .txt and .md resume files are supported in phase one.")

    return path.read_text(encoding="utf-8")


def extract_resume_skills(resume_text: str) -> list[str]:
    normalized_text = _normalize_text(resume_text)
    tokens = _tokenize(normalized_text)
    found_skills: list[str] = []

    for skill in SKILL_KEYWORDS:
        normalized_skill = _normalize_text(skill)

        if normalized_skill not in STRICT_LITERAL_SKILLS:
            continue

        if " " in normalized_skill:
            if normalized_skill in normalized_text:
                found_skills.append(skill)
        else:
            if normalized_skill in tokens:
                found_skills.append(skill)

    filtered_skills = [
        skill for skill in found_skills
        if _normalize_text(skill) not in GENERIC_SKILLS
    ]
    return _dedupe_keep_order(filtered_skills)



def extract_resume_roles(resume_text: str) -> list[str]:
    normalized_text = _normalize_text(resume_text)
    matched_roles = [role for role in ROLE_KEYWORDS if role in normalized_text]
    return _dedupe_keep_order(matched_roles)


def infer_skills_from_job(job: dict[str, Any]) -> list[str]:
    title = _normalize_text(job.get("title"))
    inferred: list[str] = []

    for pattern, skills in TITLE_INFERENCES.items():
        if pattern in title:
            inferred.extend(skills)

    explicit_skills = [
        _normalize_text(skill)
        for skill in job.get("skills", [])
        if _normalize_text(skill)
    ]

    merged = explicit_skills + inferred
    filtered = [skill for skill in merged if skill not in GENERIC_SKILLS]
    return _dedupe_keep_order(filtered)


def extract_target_keywords(jobs: list[dict[str, Any]], limit: int = 10) -> list[str]:
    keyword_counter: Counter[str] = Counter()

    for job in jobs[:limit]:
        skills = infer_skills_from_job(job)
        title = _normalize_text(job.get("title"))

        for skill in skills:
            keyword_counter[skill] += 3

        for role in ROLE_KEYWORDS:
            if role in title:
                keyword_counter[role] += 2

        for generic in ["python", "sql", "machine learning", "deep learning", "data science"]:
            if generic in title:
                keyword_counter[generic] += 1

    ranked_keywords = [keyword for keyword, _ in keyword_counter.most_common(15)]
    filtered_keywords = [keyword for keyword in ranked_keywords if _normalize_text(keyword) not in GENERIC_SKILLS]
    return _dedupe_keep_order(filtered_keywords)


def find_missing_keywords(resume_text: str, target_keywords: list[str]) -> list[str]:
    normalized_resume = _normalize_text(resume_text)
    resume_tokens = _tokenize(normalized_resume)
    missing: list[str] = []

    for keyword in target_keywords:
        variants = _expand_term(keyword)
        found = any(
            (" " in variant and variant in normalized_resume)
            or (" " not in variant and variant in resume_tokens)
            for variant in variants
        )
        if not found:
            missing.append(keyword)

    return _dedupe_keep_order(missing)


def find_buzzwords(resume_text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    for line in _split_lines(resume_text):
        normalized_line = _normalize_text(line)
        for buzzword, suggestion in BUZZWORDS.items():
            if buzzword in normalized_line:
                findings.append(
                    {
                        "line": line,
                        "buzzword": buzzword,
                        "issue": suggestion,
                    }
                )

    return findings
def classify_resume_line(line: str, index: int = 0) -> str:
    normalized_line = _normalize_text(line)

    if any(pattern in normalized_line for pattern in SOFT_SKILL_PATTERNS):
        return "soft_skill"

    if index == 0 and not _looks_like_bullet(line):
        return "summary"

    if normalized_line.startswith(tuple(WEAK_PHRASE_REPLACEMENTS.keys())):
        return "experience"

    if _looks_like_bullet(line):
        return "experience"

    return "general"


def rewrite_summary_line(line: str, missing_keywords: list[str]) -> str:
    selected_keywords = _choose_missing_keywords(missing_keywords, limit=2)
    keywords_text = ", ".join(selected_keywords) if selected_keywords else "Python and machine learning"

    return (
        f"Data-focused candidate with hands-on project experience in {keywords_text}."
    )


def rewrite_soft_skill_line(line: str) -> str:
    normalized_line = _normalize_text(line)

    if "communication" in normalized_line and "team" in normalized_line:
        return "Collaborated effectively with team members and communicated findings clearly."
    if "communication" in normalized_line:
        return "Communicated technical findings clearly through reports, presentations, and discussions."
    if "team player" in normalized_line:
        return "Collaborated effectively with cross-functional team members to complete project tasks."

    return "Demonstrated collaboration, ownership, and clear communication during project execution."


def rewrite_experience_bullet(line: str, missing_keywords: list[str]) -> str:
    cleaned_line = _clean_line_for_rewrite(line)
    cleaned_line = _ensure_action_start(cleaned_line)

    selected_keywords = _choose_missing_keywords(missing_keywords, limit=1)
    normalized_clean = _normalize_text(cleaned_line)

    if selected_keywords:
        keyword = selected_keywords[0]
        if _normalize_text(keyword) not in normalized_clean and " using " not in normalized_clean:
            cleaned_line = f"{cleaned_line} using {keyword}"

    cleaned_line = _capitalize_sentence(cleaned_line)
    if not cleaned_line.endswith("."):
        cleaned_line += "."

    return cleaned_line



def rewrite_bullet(line: str, missing_keywords: list[str]) -> str:
    return rewrite_experience_bullet(line, missing_keywords)



def suggest_summary_improvement(resume_text: str, missing_keywords: list[str]) -> str:
    extracted_skills = extract_resume_skills(resume_text)
    selected_skills = extracted_skills[:2]
    selected_missing = _choose_missing_keywords(missing_keywords, limit=2)

    skill_part = ", ".join(selected_skills) if selected_skills else "Python and machine learning"
    target_part = ", ".join(selected_missing) if selected_missing else "data science and machine learning"

    return (
        f"Data-focused candidate with hands-on experience in {skill_part}, "
        f"seeking roles aligned with {target_part}."
    )


def suggest_resume_improvements(resume_text: str, target_jobs: list[dict[str, Any]]) -> list[dict[str, str]]:
    target_keywords = extract_target_keywords(target_jobs)
    missing_keywords = find_missing_keywords(resume_text, target_keywords)

    suggestions: list[dict[str, str]] = []
    lines = _split_lines(resume_text)

    for index, line in enumerate(lines):
        normalized_line = _normalize_text(line)
        if not normalized_line:
            continue

        contains_buzzword = any(buzzword in normalized_line for buzzword in BUZZWORDS)
        weak_verb = normalized_line.startswith(tuple(WEAK_PHRASE_REPLACEMENTS.keys()))

        if not (contains_buzzword or weak_verb):
            continue

        line_type = classify_resume_line(line, index)

        if line_type == "summary":
            suggested = rewrite_summary_line(line, missing_keywords)
        elif line_type == "soft_skill":
            suggested = rewrite_soft_skill_line(line)
        else:
            suggested = rewrite_experience_bullet(line, missing_keywords)

        suggestions.append(
            {
                "original": line,
                "suggested": suggested,
            }
        )

    return suggestions



def calculate_ats_score(
    resume_text: str,
    target_jobs: list[dict[str, Any]],
) -> int:
    target_keywords = extract_target_keywords(target_jobs)
    if not target_keywords:
        return 0

    missing_keywords = find_missing_keywords(resume_text, target_keywords)
    matched_count = len(target_keywords) - len(missing_keywords)

    buzzword_penalty = min(2, len(find_buzzwords(resume_text)))
    match_score = round((matched_count / len(target_keywords)) * 10)

    return max(0, min(10, match_score - buzzword_penalty))


def analyze_resume(
    resume_text: str,
    target_jobs: list[dict[str, Any]],
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extracted_skills = extract_resume_skills(resume_text)
    extracted_roles = extract_resume_roles(resume_text)
    target_keywords = extract_target_keywords(target_jobs)
    missing_keywords = find_missing_keywords(resume_text, target_keywords)
    buzzword_findings = find_buzzwords(resume_text)
    rewrite_suggestions = suggest_resume_improvements(resume_text, target_jobs)

    recommended_skills = list(target_keywords)
    if profile:
        recommended_skills.extend(profile.get("skills", []))
        recommended_skills.extend(profile.get("preferred_roles", []))

    recommended_skills = _dedupe_keep_order(recommended_skills)
    recommended_skills = [
        skill for skill in recommended_skills if _normalize_text(skill) not in GENERIC_SKILLS
    ]

    return {
        "extracted_skills": extracted_skills,
        "extracted_roles": extracted_roles,
        "recommended_skills": recommended_skills[:15],
        "missing_keywords": missing_keywords,
        "buzzwords": buzzword_findings,
        "rewrite_suggestions": rewrite_suggestions,
        "ats_score": calculate_ats_score(resume_text, target_jobs),
    }


def print_resume_analysis(analysis: dict[str, Any]) -> None:
    print("Resume Intelligence Report")
    print(f"ATS Score: {analysis['ats_score']}/10")
    print(f"Extracted Skills: {', '.join(analysis['extracted_skills']) or 'N/A'}")
    print(f"Extracted Roles: {', '.join(analysis['extracted_roles']) or 'N/A'}")
    print(f"Recommended Skills: {', '.join(analysis['recommended_skills']) or 'N/A'}")
    print(f"Missing Keywords: {', '.join(analysis['missing_keywords']) or 'N/A'}")
    print()

    print("Buzzword Findings:")
    if analysis["buzzwords"]:
        for item in analysis["buzzwords"]:
            print(f"- {item['buzzword']}: {item['line']}")
    else:
        print("- None")
    print()

    print("Rewrite Suggestions:")
    if analysis["rewrite_suggestions"]:
        for item in analysis["rewrite_suggestions"]:
            print(f"- Original : {item['original']}")
            print(f"  Suggested: {item['suggested']}")
    else:
        print("- None")
