def is_relevant(job, profile):
    title = job["title"].lower()
    skills_text = " ".join(job["skills"]).lower()

    combined_text = title + " " + skills_text

    # Expand keywords (IMPORTANT)
    keyword_map = {
        "ml": ["machine learning"],
        "ai": ["artificial intelligence"],
        "data": ["data", "analytics", "analysis"],
    }

    # Expand user inputs
    expanded_skills = []
    for skill in profile["skills"]:
        expanded_skills.append(skill)
        if skill in keyword_map:
            expanded_skills.extend(keyword_map[skill])

    expanded_roles = []
    for role in profile["preferred_roles"]:
        expanded_roles.append(role)
        if role in keyword_map:
            expanded_roles.extend(keyword_map[role])

    # Matching
    role_match = any(role in combined_text for role in expanded_roles)
    skill_match = any(skill in combined_text for skill in expanded_skills)

    return role_match or skill_match