from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "backend") not in sys.path:
    sys.path.append(str(ROOT_DIR / "backend"))

from db import (  # noqa: E402
    get_all_applications,
    get_applications_by_status,
    init_db,
    save_application,
    save_jobs,
    update_application_status,
)
from email_utils import generate_application_email, generate_followup_email  # noqa: E402
from filter import aggregate_jobs  # noqa: E402
from resume import analyze_resume  # noqa: E402
from scraper import get_jobs  # noqa: E402


VALID_STATUSES = [
    "saved",
    "applied",
    "interview",
    "rejected",
    "offer",
    "follow_up",
]

NAV_ITEMS = [
    "Landing",
    "Find Jobs",
    "Resume Lab",
    "Application Tracker",
    "Email Studio",
]

HIRING_COMPANIES = [
    "Google",
    "Amazon",
    "Microsoft",
    "Notion",
    "Stripe",
    "OpenAI",
    "Startups Hiring Now",
    "Remote AI Teams",
]

TESTIMONIALS = [
    {
        "quote": "I stopped applying randomly. The platform showed me the roles I actually had a chance at, and the resume suggestions were instantly useful.",
        "name": "Riya S.",
        "role": "Data Science Candidate",
    },
    {
        "quote": "The application tracker and email drafts made my workflow feel organized for the first time. It feels like having a career co-pilot.",
        "name": "Arjun M.",
        "role": "ML Engineer Applicant",
    },
    {
        "quote": "Instead of juggling tabs, I could search, improve my resume, and follow up from one place. That saved me hours every week.",
        "name": "Neha K.",
        "role": "Analytics Intern Candidate",
    },
]

BLOG_TEXT = (
    "In today’s job market, candidates are overwhelmed with thousands of listings across platforms "
    "like Internshala, LinkedIn, and Naukri, yet struggle to find roles that truly match their skills. "
    "Most applicants end up applying blindly, leading to low response rates and wasted effort.\n\n"
    "Smart Job Finder AI changes this by acting as a personalized career assistant. Instead of searching "
    "manually, users simply enter their skills and preferences, and the system intelligently filters and "
    "ranks the most relevant opportunities. It not only saves time but also increases the chances of getting "
    "shortlisted by focusing on high-fit roles.\n\n"
    "Beyond job discovery, the platform helps users improve their resumes, track applications, and generate "
    "professional outreach emails — creating a complete AI-powered job hunting ecosystem."
)

HERO_IMAGE_PROMPT = (
    "A modern AI-powered career assistant dashboard, glowing UI, dark gradient background, "
    "a focused young professional working on laptop, holographic job cards floating, futuristic "
    "but realistic, cinematic lighting, minimal and premium design"
)

st.set_page_config(
    page_title="AI Job Hunter",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-top: #0b1020;
            --bg-bottom: #0f1428;
            --panel: rgba(18, 24, 45, 0.72);
            --panel-strong: rgba(17, 21, 39, 0.88);
            --border: rgba(255, 255, 255, 0.08);
            --text: #edf2ff;
            --muted: #aab5d4;
            --primary-a: #5b7cff;
            --primary-b: #8f56ff;
            --accent: #ff7a59;
            --accent-soft: #ffb189;
            --success: #2dd4bf;
            --shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
            --radius-xl: 28px;
            --radius-lg: 22px;
            --radius-md: 16px;
        }

        html, body, [class*="css"] {
            font-family: "Inter", sans-serif;
        }

        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at 10% 10%, rgba(91, 124, 255, 0.28), transparent 24%),
                radial-gradient(circle at 90% 12%, rgba(255, 122, 89, 0.22), transparent 20%),
                radial-gradient(circle at 70% 78%, rgba(143, 86, 255, 0.20), transparent 22%),
                linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(91, 124, 255, 0.24), transparent 25%),
                linear-gradient(180deg, rgba(14, 19, 35, 0.94) 0%, rgba(10, 14, 28, 0.98) 100%);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, h5 {
            color: var(--text) !important;
            letter-spacing: -0.03em;
        }

        p, label, div, span, li {
            color: var(--muted);
        }

        [data-testid="stMarkdownContainer"] p {
            color: var(--muted);
        }

        .glass-shell {
            background: var(--panel);
            border: 1px solid var(--border);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
            box-shadow: var(--shadow);
            border-radius: var(--radius-xl);
        }

        .hero-shell {
            padding: 1.2rem;
            margin-bottom: 1.25rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 1rem;
            align-items: stretch;
        }

        .hero-copy {
            padding: 1.1rem 1.1rem 0.8rem 1.1rem;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(91,124,255,0.16), rgba(143,86,255,0.16));
            border: 1px solid rgba(255,255,255,0.08);
            color: #c7d4ff !important;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .hero-title {
            margin: 1rem 0 0.8rem 0;
            font-size: 4rem;
            line-height: 0.94;
            color: #f7f9ff !important;
        }

        .hero-gradient {
            background: linear-gradient(90deg, #ffffff 0%, #cdd8ff 35%, #ffb89f 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-subtext {
            font-size: 1.05rem;
            line-height: 1.7;
            max-width: 42rem;
            color: var(--muted) !important;
        }

        .hero-cta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1rem;
        }

        .hero-pill {
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            color: #dbe5ff !important;
            font-size: 0.85rem;
        }

        .hero-visual {
            min-height: 360px;
            padding: 1rem;
            border-radius: 24px;
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 30% 20%, rgba(91,124,255,0.55), transparent 26%),
                radial-gradient(circle at 80% 24%, rgba(255,122,89,0.45), transparent 22%),
                linear-gradient(140deg, rgba(16,20,38,0.95) 0%, rgba(17,26,54,0.95) 54%, rgba(28,18,48,0.92) 100%);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .hero-visual::before {
            content: "";
            position: absolute;
            inset: auto -10% -16% 22%;
            height: 240px;
            border-radius: 28px;
            transform: rotate(-8deg);
            background: linear-gradient(135deg, rgba(255,255,255,0.14), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 30px 80px rgba(0,0,0,0.32);
        }

        .visual-panel {
            position: absolute;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 50px rgba(0,0,0,0.28);
            backdrop-filter: blur(18px);
            border-radius: 20px;
            padding: 0.9rem;
            color: #f6f8ff;
        }

        .visual-panel.top {
            top: 8%;
            left: 8%;
            width: 52%;
        }

        .visual-panel.mid {
            top: 32%;
            right: 7%;
            width: 44%;
        }

        .visual-panel.bottom {
            bottom: 10%;
            left: 12%;
            width: 58%;
        }

        .visual-badge {
            display: inline-block;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            margin-right: 0.4rem;
            background: linear-gradient(90deg, rgba(91,124,255,0.25), rgba(143,86,255,0.25));
            color: #dfe6ff !important;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 1rem 0 1.4rem 0;
        }

        .stat-card {
            padding: 1rem 1.1rem;
            border-radius: var(--radius-lg);
            background: var(--panel);
            border: 1px solid var(--border);
            backdrop-filter: blur(18px);
            box-shadow: var(--shadow);
        }

        .stat-label {
            color: #93a4d7 !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .stat-value {
            margin-top: 0.35rem;
            font-size: 2rem;
            font-weight: 800;
            color: #f4f7ff !important;
        }

        .section-card {
            padding: 1.15rem;
            margin-bottom: 1rem;
        }

        .companies-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.9rem;
            margin-top: 1rem;
        }

        .company-chip {
            padding: 1rem;
            border-radius: 18px;
            text-align: center;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.07);
            color: #e7edff !important;
            font-weight: 600;
            transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
        }

        .company-chip:hover {
            transform: translateY(-4px);
            border-color: rgba(255,255,255,0.18);
            background: rgba(255,255,255,0.08);
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }

        .feature-card {
            padding: 1.15rem;
            border-radius: 22px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.07);
        }

        .feature-kicker {
            color: #ffb38f !important;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }

        .testimonial-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }

        .testimonial-card {
            padding: 1.15rem;
            border-radius: 22px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.07);
        }

        .testimonial-quote {
            color: #f4f7ff !important;
            line-height: 1.7;
        }

        .testimonial-name {
            margin-top: 1rem;
            color: #ffffff !important;
            font-weight: 700;
        }

        .testimonial-role {
            color: #9ba9cc !important;
            font-size: 0.9rem;
        }

        .job-card {
            position: relative;
            padding: 1.15rem;
            border-radius: 24px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 12px 34px rgba(0,0,0,0.18);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            overflow: hidden;
        }

        .job-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 50px rgba(0,0,0,0.24);
            border-color: rgba(91,124,255,0.35);
        }

        .job-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 4px;
            background: linear-gradient(180deg, #5b7cff, #8f56ff, #ff7a59);
        }

        .job-company {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.8rem;
            color: #dfe6ff !important;
            font-weight: 600;
        }

        .company-badge {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(135deg, #5b7cff, #ff7a59);
            box-shadow: 0 0 18px rgba(91,124,255,0.7);
        }

        .job-meta {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 0.8rem 0 1rem 0;
        }

        .job-chip {
            border-radius: 999px;
            padding: 0.36rem 0.7rem;
            font-size: 0.8rem;
            border: 1px solid rgba(255,255,255,0.08);
            color: #e8edff !important;
            background: rgba(255,255,255,0.06);
        }

        .chip-remote {
            background: rgba(45, 212, 191, 0.16);
            color: #8bf5e4 !important;
            border-color: rgba(45, 212, 191, 0.24);
        }

        .chip-score {
            background: rgba(91, 124, 255, 0.16);
            color: #c6d3ff !important;
            border-color: rgba(91, 124, 255, 0.24);
        }

        .chip-ai {
            background: rgba(143, 86, 255, 0.16);
            color: #d8c6ff !important;
            border-color: rgba(143, 86, 255, 0.24);
        }

        .chip-ml {
            background: rgba(255, 122, 89, 0.16);
            color: #ffc5b2 !important;
            border-color: rgba(255, 122, 89, 0.24);
        }

        .resume-cta {
            padding: 1.2rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(255,122,89,0.22), transparent 20%),
                linear-gradient(135deg, rgba(91,124,255,0.12), rgba(143,86,255,0.12));
            border: 1px solid rgba(255,255,255,0.08);
            margin-top: 1rem;
        }

        .blog-card {
            padding: 1.2rem;
            border-radius: 24px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
            line-height: 1.8;
        }

        @media (max-width: 1100px) {
            .hero-grid,
            .feature-grid,
            .testimonial-grid,
            .companies-grid,
            .stats-grid {
                grid-template-columns: 1fr;
            }

            .hero-title {
                font-size: 3rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _parse_csv(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def _build_profile(skills: str, roles: str, locations: str) -> dict[str, list[str]]:
    return {
        "skills": _parse_csv(skills),
        "preferred_roles": _parse_csv(roles),
        "locations": _parse_csv(locations),
    }


def _load_ranked_jobs(profile: dict[str, list[str]]) -> list[dict]:
    jobs = get_jobs()
    ranked_jobs = aggregate_jobs(jobs, profile, limit=20)
    save_jobs(ranked_jobs)
    return ranked_jobs


def _ensure_state() -> None:
    if "ranked_jobs" not in st.session_state:
        st.session_state.ranked_jobs = []
    if "profile" not in st.session_state:
        st.session_state.profile = {}
    if "resume_analysis" not in st.session_state:
        st.session_state.resume_analysis = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Landing"
    if "sidebar_open" not in st.session_state:
        st.session_state.sidebar_open = True


def _render_sidebar() -> tuple[bool, str, str, str, str]:
    with st.sidebar:
        toggle_label = "☰ Collapse Sidebar" if st.session_state.sidebar_open else "☰ Expand Sidebar"
        if st.button(toggle_label, use_container_width=True):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()

        st.markdown("## Control Center")
        st.radio("Navigate", NAV_ITEMS, key="active_page", label_visibility="collapsed")

        if st.session_state.sidebar_open:
            st.markdown("---")
            st.markdown("### Search Profile")
            skills_input = st.text_input("Skills", placeholder="ml, ai, python, sql")
            roles_input = st.text_input("Preferred Roles", placeholder="data science, ml engineer")
            locations_input = st.text_input("Preferred Locations", placeholder="remote, bangalore")

            resume_text = st.text_area(
                "Resume Text",
                height=220,
                placeholder="Paste your resume text here for ATS analysis...",
            )

            find_jobs_clicked = st.button("Find Jobs", use_container_width=True, type="primary")
            st.caption(
                "Search, score, track, and draft outreach from one AI-powered workspace."
            )
        else:
            st.caption("Expand the sidebar to edit profile inputs and run job search.")
            skills_input = ""
            roles_input = ""
            locations_input = ""
            resume_text = ""
            find_jobs_clicked = False

    return find_jobs_clicked, skills_input, roles_input, locations_input, resume_text


def _render_hero(ranked_jobs: list[dict], tracked_count: int) -> None:
    total_jobs = len(ranked_jobs)
    avg_score = 0.0
    if ranked_jobs:
        avg_score = round(sum(job.get("score", 0) for job in ranked_jobs) / len(ranked_jobs), 1)

    st.markdown(
        f"""
        <div class="glass-shell hero-shell">
          <div class="hero-grid">
            <div class="hero-copy">
              <div class="hero-kicker">Premium AI Job Search Workspace</div>
              <h1 class="hero-title"><span class="hero-gradient">Find Your Next Job Smarter with AI</span></h1>
              <p class="hero-subtext">
                Move from scattered job boards to one intelligent workflow that discovers strong-fit roles,
                improves resumes, tracks applications, and drafts polished recruiter outreach.
              </p>
              <div class="hero-cta-row">
                <span class="hero-pill">AI-ranked opportunities</span>
                <span class="hero-pill">ATS-aware resume guidance</span>
                <span class="hero-pill">Application pipeline</span>
                <span class="hero-pill">Recruiter-ready emails</span>
              </div>
            </div>
            <div class="hero-visual">
              <div class="visual-panel top">
                <span class="visual-badge">Live Finder</span>
                <h4>Personalized role scoring</h4>
                <p>Skill-fit discovery with resume and outreach tools in one interface.</p>
              </div>
              <div class="visual-panel mid">
                <span class="visual-badge">AI Workspace</span>
                <h4>Career assistant flow</h4>
                <p>Holographic cards, premium UI, and a focused workflow feel.</p>
              </div>
              <div class="visual-panel bottom">
                <span class="visual-badge">Visual Direction</span>
                <p>{HERO_IMAGE_PROMPT}</p>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Total Jobs</div>
            <div class="stat-value">{total_jobs}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Matches</div>
            <div class="stat-value">{total_jobs}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Avg Score</div>
            <div class="stat-value">{avg_score}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hiring_companies() -> None:
    chips = "".join(f'<div class="company-chip">{company}</div>' for company in HIRING_COMPANIES)
    st.markdown(
        f"""
        <div class="glass-shell section-card">
          <h3>Hiring Companies</h3>
          <p>Explore roles inspired by top product companies, AI teams, and fast-moving startups.</p>
          <div class="companies-grid">
            {chips}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_resume_cta() -> None:
    st.markdown(
        """
        <div class="resume-cta">
          <h3>Analyze & Improve Resume</h3>
          <p>Turn a generic resume into a stronger, ATS-aware document with missing keyword insights and better rewrite suggestions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Analyze & Improve Resume", type="primary"):
        st.session_state.active_page = "Resume Lab"
        st.rerun()


def _render_testimonials() -> None:
    cards = ""
    for item in TESTIMONIALS:
        cards += f"""
        <div class="testimonial-card">
          <p class="testimonial-quote">“{item['quote']}”</p>
          <div class="testimonial-name">{item['name']}</div>
          <div class="testimonial-role">{item['role']}</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="glass-shell section-card">
          <h3>What users would say</h3>
          <div class="testimonial-grid">
            {cards}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_blog_section() -> None:
    blog_html = BLOG_TEXT.replace("\n\n", "<br><br>")
    st.markdown(
        f"""
        <div class="glass-shell section-card">
          <h3>Why Smart Job Finder AI matters</h3>
          <div class="blog-card">
            {blog_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _job_tags(job: dict) -> str:
    tags = []
    location = str(job.get("location", "")).lower()
    title = str(job.get("title", "")).lower()
    skills = [str(skill).lower() for skill in job.get("skills", [])]

    if "remote" in location or job.get("type") == "Remote":
        tags.append('<span class="job-chip chip-remote">Remote</span>')
    if "ai" in title or "artificial intelligence" in title or "artificial intelligence" in skills:
        tags.append('<span class="job-chip chip-ai">AI</span>')
    if "ml" in title or "machine learning" in title or "machine learning" in skills:
        tags.append('<span class="job-chip chip-ml">ML</span>')

    tags.append(f'<span class="job-chip chip-score">Score {job["score"]}</span>')
    tags.append(f'<span class="job-chip">{job["source"]}</span>')
    return "".join(tags)


def _render_job_card(job: dict, index: int) -> None:
    skills_text = ", ".join(job["skills"]) if job["skills"] else "N/A"

    st.markdown(
        f"""
        <div class="job-card">
          <h3>{index}. {job['title']}</h3>
          <div class="job-company"><span class="company-badge"></span>{job['company']}</div>
          <div class="job-meta">
            <span class="job-chip">{job['location']}</span>
            <span class="job-chip">{job['type']}</span>
            {_job_tags(job)}
          </div>
          <p><strong>Skills:</strong> {skills_text}</p>
          <p><strong>Salary:</strong> {job['salary']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Open Job", job["link"], use_container_width=False)


def _render_resume_analysis(analysis: dict) -> None:
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.8, 1.1, 1.1])
        with col1:
            st.metric("ATS Score", f"{analysis['ats_score']}/10")
        with col2:
            st.markdown("**Recommended Skills**")
            st.write(", ".join(analysis["recommended_skills"]) or "N/A")
        with col3:
            st.markdown("**Missing Keywords**")
            st.write(", ".join(analysis["missing_keywords"]) or "N/A")

        left, right = st.columns(2)
        with left:
            st.markdown("**Extracted Skills**")
            st.write(", ".join(analysis["extracted_skills"]) or "N/A")

            st.markdown("**Extracted Roles**")
            st.write(", ".join(analysis["extracted_roles"]) or "N/A")

        with right:
            st.markdown("**Buzzword Findings**")
            if analysis["buzzwords"]:
                for item in analysis["buzzwords"]:
                    st.write(f"- **{item['buzzword']}**: {item['line']}")
            else:
                st.write("None")

        st.markdown("**Rewrite Suggestions**")
        if analysis["rewrite_suggestions"]:
            for item in analysis["rewrite_suggestions"]:
                with st.expander(item["original"]):
                    st.write(item["suggested"])
        else:
            st.write("No rewrite suggestions available.")


def _render_applications(status_filter: str) -> None:
    applications = get_all_applications() if status_filter == "all" else get_applications_by_status(status_filter)

    if not applications:
        st.info("No tracked applications found.")
        return

    for index, app in enumerate(applications, start=1):
        with st.container(border=True):
            st.markdown(f"### {index}. {app.get('title', 'N/A')}")
            st.write(f"**Company:** {app.get('company', 'N/A')}")
            st.write(f"**Status:** {app.get('status', 'N/A')}")
            st.write(f"**Location:** {app.get('location', 'N/A')}")
            st.write(f"**Source:** {app.get('source', 'N/A')}")
            st.write(f"**Score:** {app.get('score', 'N/A')}")
            st.write(f"**Notes:** {app.get('notes', '') or 'N/A'}")
            st.write(f"**Applied At:** {app.get('applied_at', 'N/A') or 'N/A'}")
            st.write(f"**Updated At:** {app.get('updated_at', 'N/A')}")
            st.link_button("Open Tracked Job", app.get("job_link", "#"), key=f"tracked_job_{index}")


def _render_email_draft(job: dict, profile: dict[str, list[str]], draft_type: str) -> None:
    draft = generate_application_email(job, profile) if draft_type == "application" else generate_followup_email(job, profile)

    with st.container(border=True):
        st.markdown("### Subject")
        st.code(draft["subject"], language=None)

        st.markdown("### Body")
        st.text_area("Email Body", value=draft["body"], height=320, label_visibility="collapsed")


def _save_application_status(job: dict, status: str, notes: str) -> None:
    if not status:
        return

    save_application(job["link"], status=status, notes=notes)
    update_application_status(job["link"], status=status, notes=notes)


def main() -> None:
    init_db()
    _ensure_state()
    _inject_styles()

    find_jobs_clicked, skills_input, roles_input, locations_input, resume_text = _render_sidebar()

    if find_jobs_clicked:
        profile = _build_profile(skills_input, roles_input, locations_input)
        ranked_jobs = _load_ranked_jobs(profile)

        st.session_state.profile = profile
        st.session_state.ranked_jobs = ranked_jobs
        st.session_state.resume_analysis = (
            analyze_resume(resume_text, ranked_jobs[:5], profile)
            if resume_text.strip() and ranked_jobs
            else None
        )
        st.session_state.active_page = "Find Jobs"

    ranked_jobs = st.session_state.ranked_jobs
    profile = st.session_state.profile
    resume_analysis = st.session_state.resume_analysis
    tracked_applications = get_all_applications()

    _render_hero(ranked_jobs, len(tracked_applications))

    page = st.session_state.get("active_page", "Landing")

    if page == "Landing":
        _render_hiring_companies()
        _render_resume_cta()

        st.markdown(
            """
            <div class="glass-shell section-card">
              <h3>Product Overview</h3>
              <div class="feature-grid">
                <div class="feature-card">
                  <div class="feature-kicker">Discover</div>
                  <h4>AI-ranked job search</h4>
                  <p>Filter and rank opportunities based on profile fit instead of manually scanning noisy listings.</p>
                </div>
                <div class="feature-card">
                  <div class="feature-kicker">Improve</div>
                  <h4>Resume intelligence</h4>
                  <p>Find weak phrasing, missing ATS keywords, and sharper rewrite suggestions for stronger shortlisting potential.</p>
                </div>
                <div class="feature-card">
                  <div class="feature-kicker">Convert</div>
                  <h4>Track and reach out</h4>
                  <p>Move applications through stages and generate professional recruiter emails from one premium workspace.</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _render_blog_section()
        _render_testimonials()

    elif page == "Find Jobs":
        st.markdown(
            """
            <div class="glass-shell section-card">
              <h2>Find Jobs</h2>
              <p>Explore ranked opportunities and save application status directly from the card flow.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not ranked_jobs:
            st.info("Use the sidebar profile inputs and click Find Jobs to populate this workspace.")
        else:
            for index, job in enumerate(ranked_jobs[:10], start=1):
                _render_job_card(job, index)

                col1, col2, col3 = st.columns([1, 1.8, 0.8])
                with col1:
                    status = st.selectbox(
                        f"Status for job {index}",
                        options=[""] + VALID_STATUSES,
                        key=f"status_{index}",
                    )
                with col2:
                    notes = st.text_input(
                        f"Notes for job {index}",
                        key=f"notes_{index}",
                        placeholder="Optional notes about next steps",
                    )
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("Save", key=f"save_status_{index}", use_container_width=True):
                        if status:
                            _save_application_status(job, status, notes)
                            st.success(f"Saved '{status}' for {job['title']}.")
                        else:
                            st.warning("Please select a status first.")

    elif page == "Resume Lab":
        st.markdown(
            """
            <div class="glass-shell section-card">
              <h2>Resume Lab</h2>
              <p>Review ATS scoring, missing keywords, buzzword findings, and better rewrite suggestions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not resume_analysis:
            st.info("Paste resume text in the sidebar and run a search to unlock the Resume Lab.")
        else:
            _render_resume_analysis(resume_analysis)

    elif page == "Application Tracker":
        st.markdown(
            """
            <div class="glass-shell section-card">
              <h2>Application Tracker</h2>
              <p>Review your pipeline and filter applications by stage.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        status_filter = st.selectbox(
            "Filter by status",
            options=["all"] + VALID_STATUSES,
            index=0,
        )
        _render_applications(status_filter)

    elif page == "Email Studio":
        st.markdown(
            """
            <div class="glass-shell section-card">
              <h2>Email Studio</h2>
              <p>Generate polished application and follow-up drafts for your selected role.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not ranked_jobs:
            st.info("Run a search first to generate email drafts.")
        else:
            job_labels = [
                f"{index + 1}. {job['title']} - {job['company']}"
                for index, job in enumerate(ranked_jobs[:10])
            ]
            selected_label = st.selectbox("Choose a job", options=job_labels)
            selected_index = job_labels.index(selected_label)
            selected_job = ranked_jobs[selected_index]

            draft_type = st.radio(
                "Draft type",
                options=["application", "followup"],
                horizontal=True,
            )
            _render_email_draft(selected_job, profile, draft_type)


if __name__ == "__main__":
    main()
