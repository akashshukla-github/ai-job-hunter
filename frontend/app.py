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
    {"name": "Google", "url": "https://www.google.com/about/careers/applications/jobs/results/", "logo": "G"},
    {"name": "Amazon", "url": "https://www.amazon.jobs/", "logo": "A"},
    {"name": "Microsoft", "url": "https://jobs.careers.microsoft.com/global/en", "logo": "M"},
    {"name": "Notion", "url": "https://www.notion.so/careers", "logo": "N"},
    {"name": "Stripe", "url": "https://stripe.com/jobs", "logo": "S"},
    {"name": "OpenAI", "url": "https://openai.com/careers/", "logo": "O"},
    {"name": "Startups", "url": "https://wellfound.com/jobs", "logo": "SU"},
    {"name": "Remote AI Teams", "url": "https://remoteok.com/remote-ai-jobs", "logo": "R"},
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

NEWS_FEED = [
    {
        "title": "AI hiring remains strongest in product, ML, and data roles",
        "summary": "Companies are prioritizing practical AI execution roles that blend business context with automation and modeling skills.",
        "link": "https://example.com/ai-hiring-market",
    },
    {
        "title": "Remote-first startups continue opening high-fit AI jobs",
        "summary": "Specialized teams are still hiring remote candidates for LLM apps, analytics, and workflow automation products.",
        "link": "https://example.com/remote-ai-jobs",
    },
    {
        "title": "Recruiters are using skills-first screening more than degree filters",
        "summary": "Applicants with sharp project proof, strong resumes, and portfolio signal are getting better response rates.",
        "link": "https://example.com/skills-first-screening",
    },
    {
        "title": "Resume personalization is becoming a competitive advantage",
        "summary": "Candidates tailoring resumes to role intent and keyword coverage are seeing stronger shortlisting performance.",
        "link": "https://example.com/resume-personalization",
    },
]

TRENDING_ROLES = [
    "Applied AI Engineer",
    "Data Scientist",
    "ML Engineer",
    "AI Product Manager",
    "Prompt Engineer",
    "Analytics Engineer",
]

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
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-deep: #050814;
            --bg-mid: #0e1531;
            --bg-purple: #1d1042;
            --bg-black: #04060d;
            --panel: rgba(16, 22, 42, 0.72);
            --panel-soft: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.10);
            --text: #f4f7ff;
            --muted: #a6b0d7;
            --blue: #62adff;
            --purple: #a26cff;
            --orange: #ff9d57;
            --green: #34d6a0;
            --shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
            --glow: 0 0 0 1px rgba(255,255,255,0.02), 0 0 32px rgba(98, 173, 255, 0.14);
            --radius-xl: 28px;
            --radius-lg: 22px;
            --radius-md: 18px;
        }

        html {
            scroll-behavior: smooth;
        }

        html, body, [class*="css"] {
            font-family: "Manrope", sans-serif;
        }

        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at 8% 10%, rgba(98, 173, 255, 0.22), transparent 24%),
                radial-gradient(circle at 90% 12%, rgba(162, 108, 255, 0.18), transparent 24%),
                radial-gradient(circle at 72% 80%, rgba(255, 157, 87, 0.16), transparent 20%),
                linear-gradient(135deg, var(--bg-mid) 0%, var(--bg-purple) 46%, var(--bg-black) 100%);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(98, 173, 255, 0.15), transparent 28%),
                linear-gradient(180deg, rgba(8, 12, 26, 0.96) 0%, rgba(10, 13, 28, 0.98) 100%);
            border-right: 1px solid var(--border);
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }

        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            font-family: "Space Grotesk", sans-serif;
            letter-spacing: -0.03em;
        }

        p, label, div, span, li {
            color: var(--muted);
        }

        [data-testid="stMarkdownContainer"] p {
            color: var(--muted);
        }

        .glass-shell,
        .hero-shell,
        .metric-shell,
        .section-card,
        .news-shell,
        .feature-card,
        .job-card,
        .testimonial-card,
        .resume-cta,
        .company-tile {
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border: 1px solid var(--border);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: var(--shadow), var(--glow);
        }

        .hero-shell {
            border-radius: var(--radius-xl);
            padding: 1.25rem;
            margin-bottom: 1.1rem;
            overflow: hidden;
            position: relative;
        }

        .hero-shell::before {
            content: "";
            position: absolute;
            inset: auto -6% -34% auto;
            width: 320px;
            height: 320px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(98,173,255,0.30), transparent 64%);
            filter: blur(18px);
        }

        .topbar-shell {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 1rem;
            align-items: stretch;
        }

        .hero-copy {
            padding: 1rem 1rem 0.8rem 1rem;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 1rem;
            border-radius: 999px;
            background: rgba(98, 173, 255, 0.14);
            border: 1px solid rgba(98, 173, 255, 0.26);
            box-shadow: 0 0 28px rgba(98, 173, 255, 0.25);
            color: #deebff !important;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        .hero-title {
            margin: 1rem 0 0.85rem 0;
            font-size: clamp(2.8rem, 5vw, 4.8rem);
            line-height: 0.95;
            font-weight: 800;
            letter-spacing: -0.05em;
        }

        .hero-gradient {
            background: linear-gradient(90deg, var(--blue) 0%, var(--purple) 54%, var(--orange) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-subtext {
            font-size: 1.04rem;
            line-height: 1.8;
            max-width: 44rem;
            color: var(--muted) !important;
        }

        .hero-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1.15rem;
        }

        .hero-pill {
            padding: 0.6rem 0.95rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            color: #e3ebff !important;
            font-size: 0.84rem;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }

        .hero-pill:hover,
        .feature-card:hover,
        .job-card:hover,
        .company-tile:hover,
        .metric-shell:hover,
        .testimonial-card:hover {
            transform: translateY(-4px);
            border-color: rgba(162, 108, 255, 0.26);
            box-shadow: 0 26px 60px rgba(0,0,0,0.34), 0 0 28px rgba(162,108,255,0.14);
        }

        .hero-visual {
            min-height: 380px;
            padding: 1rem;
            border-radius: 24px;
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 30% 18%, rgba(98,173,255,0.40), transparent 26%),
                radial-gradient(circle at 82% 22%, rgba(255,157,87,0.30), transparent 20%),
                linear-gradient(145deg, rgba(10,14,28,0.94) 0%, rgba(17,22,48,0.96) 54%, rgba(24,14,42,0.92) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
        }

        .hero-visual::before {
            content: "";
            position: absolute;
            inset: auto -12% -18% 18%;
            height: 240px;
            border-radius: 28px;
            transform: rotate(-8deg);
            background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.03));
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
            padding: 0.95rem;
            color: #f6f8ff;
        }

        .visual-panel.top {
            top: 8%;
            left: 8%;
            width: 54%;
        }

        .visual-panel.mid {
            top: 34%;
            right: 7%;
            width: 42%;
        }

        .visual-panel.bottom {
            bottom: 10%;
            left: 10%;
            width: 60%;
        }

        .visual-badge {
            display: inline-block;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            margin-right: 0.4rem;
            background: linear-gradient(90deg, rgba(98,173,255,0.24), rgba(162,108,255,0.24));
            color: #dfe6ff !important;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin: 1rem 0 1.2rem 0;
        }

        .metric-shell {
            padding: 1rem 1.05rem;
            border-radius: 22px;
            min-height: 138px;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .metric-icon {
            width: 42px;
            height: 42px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            background: linear-gradient(135deg, rgba(98,173,255,0.22), rgba(162,108,255,0.22));
            margin-bottom: 0.8rem;
        }

        .metric-label {
            color: #95a5d7 !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.74rem;
            font-weight: 700;
        }

        .metric-value {
            margin-top: 0.35rem;
            font-size: 1.85rem;
            font-weight: 800;
            color: #f4f7ff !important;
        }

        .section-card {
            padding: 1.15rem;
            border-radius: var(--radius-xl);
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .section-copy {
            color: var(--muted) !important;
            line-height: 1.75;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 0.95rem;
        }

        .feature-card {
            padding: 1.1rem;
            border-radius: 22px;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .feature-kicker {
            color: #ffb38f !important;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .feature-title {
            color: #ffffff !important;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }

        .feature-copy {
            color: var(--muted) !important;
            line-height: 1.7;
            font-size: 0.94rem;
        }

        .companies-scroll {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.9rem;
            margin-top: 1rem;
        }

        .company-link {
            text-decoration: none !important;
        }

        .company-tile {
            border-radius: 22px;
            padding: 1rem;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .company-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.8rem;
        }

        .company-logo {
            width: 50px;
            height: 50px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #ffffff !important;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .company-name {
            color: #f2f6ff !important;
            font-weight: 800;
        }

        .company-sub {
            color: #96a4cf !important;
            font-size: 0.85rem;
        }

        .company-badge-live {
            display: inline-flex;
            width: fit-content;
            padding: 0.36rem 0.65rem;
            border-radius: 999px;
            background: rgba(52, 214, 160, 0.14);
            border: 1px solid rgba(52, 214, 160, 0.24);
            color: #b7ffe3 !important;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .resume-cta {
            padding: 1.25rem;
            border-radius: 24px;
            background:
                radial-gradient(circle at top right, rgba(255,157,87,0.18), transparent 18%),
                linear-gradient(135deg, rgba(98,173,255,0.12), rgba(162,108,255,0.12));
            margin-top: 0.8rem;
        }

        .resume-kicker {
            display: inline-block;
            margin-bottom: 0.55rem;
            padding: 0.34rem 0.7rem;
            border-radius: 999px;
            background: rgba(98,173,255,0.12);
            border: 1px solid rgba(98,173,255,0.2);
            color: #dce9ff !important;
            font-size: 0.76rem;
            font-weight: 700;
        }

        .resume-headline {
            font-size: 1.9rem;
            line-height: 1.1;
            margin-bottom: 0.45rem;
        }

        .blog-card {
            padding: 1.2rem;
            border-radius: 24px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
            line-height: 1.8;
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
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .testimonial-quote {
            color: #f4f7ff !important;
            line-height: 1.75;
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

        .news-shell {
            padding: 1.15rem;
            border-radius: 26px;
            min-height: 100%;
            height: 100%;
        }

        .news-title-main {
            font-size: 1.25rem;
            font-weight: 800;
            color: #f8fbff !important;
            margin-bottom: 0.4rem;
        }

        .news-copy {
            color: var(--muted) !important;
            margin-bottom: 0.9rem;
            line-height: 1.7;
        }

        .news-scroll {
            max-height: 840px;
            overflow-y: auto;
            padding-right: 0.15rem;
        }

        .news-scroll::-webkit-scrollbar {
            width: 6px;
        }

        .news-scroll::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.18);
            border-radius: 99px;
        }

        .news-item {
            padding: 1rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.8rem;
            transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
        }

        .news-item:hover {
            transform: translateX(3px);
            border-color: rgba(98,173,255,0.28);
            box-shadow: 0 16px 30px rgba(0,0,0,0.18);
        }

        .news-item-title {
            color: #ffffff !important;
            font-weight: 800;
            line-height: 1.45;
            margin-bottom: 0.4rem;
        }

        .news-item-summary {
            color: var(--muted) !important;
            line-height: 1.7;
            font-size: 0.92rem;
            margin-bottom: 0.55rem;
        }

        .news-link {
            color: #9fcdff !important;
            font-weight: 700;
            text-decoration: none;
        }

        .job-card {
            position: relative;
            padding: 1.15rem;
            border-radius: 24px;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
            overflow: hidden;
            margin-bottom: 0.8rem;
        }

        .job-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 4px;
            background: linear-gradient(180deg, var(--blue), var(--purple), var(--orange));
        }

        .job-top {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-start;
        }

        .job-title-main {
            font-size: 1.18rem;
            font-weight: 800;
            color: #f7f9ff !important;
            margin-bottom: 0.35rem;
        }

        .job-company-row {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.9rem;
            color: #dfe6ff !important;
            font-weight: 700;
        }

        .company-badge {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--blue), var(--orange));
            box-shadow: 0 0 18px rgba(98,173,255,0.7);
        }

        .salary-pill {
            white-space: nowrap;
            padding: 0.45rem 0.75rem;
            border-radius: 14px;
            background: rgba(255, 157, 87, 0.12);
            border: 1px solid rgba(255, 157, 87, 0.22);
            color: #ffd7bb !important;
            font-weight: 800;
            font-size: 0.95rem;
        }

        .job-meta,
        .skill-tag-row {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 0.75rem 0 0.9rem 0;
        }

        .job-chip,
        .skill-chip {
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            font-size: 0.8rem;
            border: 1px solid rgba(255,255,255,0.08);
            color: #e8edff !important;
            background: rgba(255,255,255,0.06);
        }

        .chip-remote {
            background: rgba(52, 214, 160, 0.14);
            color: #aaf5dd !important;
            border-color: rgba(52, 214, 160, 0.24);
        }

        .chip-score {
            background: rgba(98, 173, 255, 0.14);
            color: #d1ddff !important;
            border-color: rgba(98, 173, 255, 0.24);
        }

        .chip-ai {
            background: rgba(162, 108, 255, 0.14);
            color: #decfff !important;
            border-color: rgba(162, 108, 255, 0.24);
        }

        .chip-ml {
            background: rgba(255, 157, 87, 0.14);
            color: #ffd3b8 !important;
            border-color: rgba(255, 157, 87, 0.24);
        }

        .skill-chip {
            background: linear-gradient(135deg, rgba(98,173,255,0.15), rgba(162,108,255,0.15));
            border-color: rgba(98,173,255,0.18);
        }

        .job-description {
            color: var(--muted) !important;
            line-height: 1.75;
        }

        .tracker-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 1rem;
        }

        .search-wrap [data-testid="stTextInputRootElement"] {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.22);
            transition: box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .search-wrap [data-testid="stTextInputRootElement"]:focus-within {
            border-color: rgba(98,173,255,0.45);
            box-shadow: 0 0 0 1px rgba(98,173,255,0.30), 0 0 28px rgba(98,173,255,0.22);
        }

        .search-wrap input {
            color: white !important;
            font-size: 0.98rem !important;
        }

        .search-wrap input::placeholder {
            color: #8d99bf !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
            border-radius: 14px !important;
            border: 1px solid rgba(98,173,255,0.22) !important;
            background: linear-gradient(90deg, rgba(98,173,255,0.18), rgba(162,108,255,0.18)) !important;
            color: white !important;
            font-weight: 700 !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
            box-shadow: 0 12px 28px rgba(0,0,0,0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stLinkButton > a:hover {
            transform: translateY(-2px);
            border-color: rgba(255,157,87,0.28) !important;
            box-shadow: 0 18px 38px rgba(98,173,255,0.18);
        }

        .stSelectbox div[data-baseweb="select"] > div,
        .stTextInput input,
        .stTextArea textarea {
            background-color: rgba(255,255,255,0.06) !important;
            color: #f1f5ff !important;
            border-radius: 14px !important;
        }

        .stRadio > div,
        .stCheckbox > label {
            color: var(--text) !important;
        }

        .subtle-anchor a {
            color: #9fcdff !important;
            text-decoration: none;
            font-weight: 700;
        }

        .page-shell {
            padding-bottom: 1rem;
        }

        .footer-note {
            text-align: center;
            color: #8e97b9 !important;
            font-size: 0.88rem;
            margin-top: 1rem;
        }

        @media (max-width: 1180px) {
            .hero-grid,
            .feature-grid,
            .testimonial-grid,
            .companies-scroll,
            .metric-grid {
                grid-template-columns: 1fr;
            }

            .hero-title {
                font-size: 3rem;
            }
        }
            /* 🔥 Fix input text visibility */
    input, textarea {
        color: black !important;
    }

    input::placeholder, textarea::placeholder {
        color: #888 !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        color: black !important;
        background-color: #f2f2f2 !important;
    }

    .stSelectbox div {
        color: black !important;
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


def _safe_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _safe_text(value: object, fallback: str = "N/A") -> str:
    text = str(value).strip() if value is not None else ""
    return text if text else fallback


def _normalize_job(job: dict) -> dict:
    normalized = dict(job)
    normalized["title"] = _safe_text(job.get("title"))
    normalized["company"] = _safe_text(job.get("company"))
    normalized["location"] = _safe_text(job.get("location"))
    normalized["type"] = _safe_text(job.get("type", "Unknown"))
    normalized["salary"] = _safe_text(job.get("salary", "Compensation not listed"))
    normalized["source"] = _safe_text(job.get("source", "Source"))
    normalized["link"] = _safe_text(job.get("link", "#"), "#")
    normalized["skills"] = _safe_list(job.get("skills"))
    normalized["score"] = job.get("score", 0)
    return normalized


def _load_ranked_jobs(profile: dict[str, list[str]]) -> list[dict]:
    jobs = get_jobs()
    ranked_jobs = aggregate_jobs(jobs, profile, limit=20)
    ranked_jobs = [_normalize_job(job) for job in ranked_jobs]
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
    if "global_search" not in st.session_state:
        st.session_state.global_search = ""


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
            st.caption("Search, score, track, and draft outreach from one AI-powered workspace.")
        else:
            st.caption("Expand the sidebar to edit profile inputs and run job search.")
            skills_input = ""
            roles_input = ""
            locations_input = ""
            resume_text = ""
            find_jobs_clicked = False

    return find_jobs_clicked, skills_input, roles_input, locations_input, resume_text


def _render_brand_header():
    st.markdown(
        """
        <style>
        .brand-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.4rem 0 0.8rem 0;
        }

        .brand-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-logo {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #62adff, #a26cff, #ff9d57);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: white;
            font-size: 1.2rem;
            box-shadow: 0 0 18px rgba(98,173,255,0.6);
        }

        .brand-name {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(90deg, #62adff, #a26cff, #ff9d57);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-tagline {
            font-size: 0.8rem;
            color: #8fa2d9;
            margin-top: -2px;
        }

        .brand-stack {
            display: flex;
            flex-direction: column;
        }
        </style>

        <div class="brand-bar">
            <div class="brand-left">
                <div class="brand-logo">H</div>
                <div class="brand-stack">
                    <div class="brand-name">Herald.ai</div>
                    <div class="brand-tagline">AI Career Intelligence Engine</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _render_topbar_search() -> str:
    st.markdown('<div class="topbar-shell">', unsafe_allow_html=True)

    col1, col2 = st.columns([2.8, 2.2])

    with col1:
        _render_brand_header()  # 👈 ADD THIS LINE

    with col2:
        st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
        query = st.text_input(
            "Global Search",
            value=st.session_state.get("global_search", ""),
            placeholder="Search jobs, companies, skills…",
            label_visibility="collapsed",
            key="global_search_input",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.global_search = query
    return query


def _filter_jobs_by_query(jobs: list[dict], query: str) -> list[dict]:
    if not query.strip():
        return jobs

    q = query.lower().strip()
    filtered = []
    for job in jobs:
        skills = " ".join(_safe_list(job.get("skills")))
        haystack = " ".join(
            [
                _safe_text(job.get("title"), ""),
                _safe_text(job.get("company"), ""),
                _safe_text(job.get("location"), ""),
                _safe_text(job.get("type"), ""),
                _safe_text(job.get("salary"), ""),
                _safe_text(job.get("source"), ""),
                skills,
            ]
        ).lower()
        if q in haystack:
            filtered.append(job)
    return filtered


def _derive_metrics(ranked_jobs: list[dict], tracked_count: int) -> dict[str, str]:
    total_jobs = len(ranked_jobs)
    avg_score = round(sum(float(job.get("score", 0)) for job in ranked_jobs) / total_jobs, 1) if total_jobs else 0
    top_score = max((float(job.get("score", 0)) for job in ranked_jobs), default=0)
    applied_count = 0
    try:
        applied_count = len(get_applications_by_status("applied"))
    except Exception:
        applied_count = 0

    success_rate = round((applied_count / tracked_count) * 100, 1) if tracked_count else 0
    return {
        "total_jobs": str(total_jobs),
        "matches": str(total_jobs),
        "avg_score": str(avg_score),
        "top_score": f"{top_score:.0f}%",
        "success_rate": f"{success_rate:.0f}%",
    }


def _render_hero(metrics: dict[str, str]) -> None:
    st.markdown(
        f"""
        <div class="hero-shell">
          <div class="hero-grid">
            <div class="hero-copy">
              <div class="hero-badge">AI Career Engine</div>
              <h1 class="hero-title"><span class="hero-gradient">Design Your Career with AI Intelligence</span></h1>
              <p class="hero-subtext">
                Stop searching through noise. Discover the right roles faster, strengthen your resume with AI feedback,
                track every application, and send sharper outreach from one premium career platform built to create momentum.
              </p>
              <div class="hero-pill-row">
                <span class="hero-pill">AI-ranked opportunities</span>
                <span class="hero-pill">ATS-aware resume guidance</span>
                <span class="hero-pill">Application pipeline</span>
                <span class="hero-pill">Recruiter-ready emails</span>
              </div>
            </div>
            <div class="hero-visual">
              <div class="visual-panel top">
                <span class="visual-badge">Live Finder</span>
                <h4>Stop searching. Start getting matched.</h4>
                <p>Role discovery, scoring, resume intelligence, and email workflows in one premium workspace.</p>
              </div>
              <div class="visual-panel mid">
                <span class="visual-badge">Smart Layer</span>
                <h4>Focused career momentum</h4>
                <p>Designed to help candidates move with more signal, less guessing, and stronger fit.</p>
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
        <div class="metric-grid">
          <div class="metric-shell">
            <div class="metric-icon">📌</div>
            <div class="metric-label">Live Opportunities</div>
            <div class="metric-value">{metrics['total_jobs']}</div>
          </div>
          <div class="metric-shell">
            <div class="metric-icon">🎯</div>
            <div class="metric-label">Top Match Score</div>
            <div class="metric-value">{metrics['top_score']}</div>
          </div>
          <div class="metric-shell">
            <div class="metric-icon">⚡</div>
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">{metrics['success_rate']}</div>
          </div>
          <div class="metric-shell">
            <div class="metric-icon">📨</div>
            <div class="metric-label">Tracked Pipeline</div>
            <div class="metric-value">{metrics['matches']}</div>
          </div>
          <div class="metric-shell">
            <div class="metric-icon">📊</div>
            <div class="metric-label">Average Score</div>
            <div class="metric-value">{metrics['avg_score']}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_news_panel() -> None:
    items = "".join(
        f"""
        <div class="news-item">
          <div class="news-item-title">{item['title']}</div>
          <div class="news-item-summary">{item['summary']}</div>
          <a class="news-link" href="{item['link']}" target="_blank">Read insight</a>
        </div>
        """
        for item in NEWS_FEED
    )

    st.markdown(
        f"""
        <div class="news-shell">
          <div class="news-title-main">Live AI Job Market Insights</div>
          <div class="news-copy">NewsAPI-ready structure with premium glass styling, quick summaries, and clickable links.</div>
          <div class="news-scroll">
            {items}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_feature_highlights(profile: dict[str, list[str]], ranked_jobs: list[dict]) -> None:
    target_skills = set(skill.lower() for skill in profile.get("skills", []))
    role_skills = set()
    for job in ranked_jobs[:8]:
        for skill in _safe_list(job.get("skills")):
            role_skills.add(skill.lower())

    missing = [skill.title() for skill in sorted(role_skills - target_skills)[:4]]
    missing_text = ", ".join(missing) if missing else "Add more role-specific keywords to sharpen match quality."

    recommended_company = ranked_jobs[0]["company"] if ranked_jobs else "top AI-first teams"
    recent_titles = ", ".join(job["title"] for job in ranked_jobs[:3]) if ranked_jobs else "Fresh roles will appear after your first search."
    trending_html = "".join([f'<span class="job-chip chip-ai">{role}</span>' for role in TRENDING_ROLES[:5]])

    st.markdown(
        f"""
        <div class="section-card">
          <div class="section-title">Career Momentum Layer</div>
          <div class="section-copy">Additional premium insights to help users act faster and make stronger decisions.</div>
          <div class="feature-grid">
            <div class="feature-card">
              <div class="feature-kicker">Trending Roles</div>
              <div class="feature-title">What’s hot right now</div>
              <div class="feature-copy">{trending_html}</div>
            </div>
            <div class="feature-card">
              <div class="feature-kicker">Skill Gap Insight</div>
              <div class="feature-title">What to strengthen next</div>
              <div class="feature-copy">{missing_text}</div>
            </div>
            <div class="feature-card">
              <div class="feature-kicker">Recommended for You</div>
              <div class="feature-title">Best-fit direction</div>
              <div class="feature-copy">Based on your inputs, focus first on opportunities from {recommended_company} and similar teams with strong alignment.</div>
            </div>
            <div class="feature-card">
              <div class="feature-kicker">Recently Added Jobs</div>
              <div class="feature-title">Fresh opportunities</div>
              <div class="feature-copy">{recent_titles}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hiring_companies() -> None:
    chips = "".join(
        f"""
        <a class="company-link" href="{company['url']}" target="_blank">
          <div class="company-tile">
            <div class="company-head">
              <div class="company-logo">{company['logo']}</div>
              <div class="company-badge-live">Hiring Now</div>
            </div>
            <div>
              <div class="company-name">{company['name']}</div>
              <div class="company-sub">Open careers ↗</div>
            </div>
          </div>
        </a>
        """
        for company in HIRING_COMPANIES
    )

    st.markdown(
        f"""
        <div class="section-card">
          <div class="section-title">Hiring Companies</div>
          <div class="section-copy">Explore live career pages from top product companies, AI teams, and fast-moving startups.</div>
          <div class="companies-scroll">
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
          <div class="resume-kicker">Resume Lab</div>
          <div class="resume-headline">Your Resume Might Be Holding You Back</div>
          <p>Uncover weak phrasing, missing ATS keywords, and sharper rewrites before the next application slips past you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([0.9, 1.2])
    with col1:
        if st.button("Analyze Resume Now", type="primary", use_container_width=True):
            st.session_state.active_page = "Resume Lab"
            st.rerun()
    with col2:
        st.markdown('<div class="subtle-anchor"><a href="#resume-lab">Jump to Resume Lab</a></div>', unsafe_allow_html=True)


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
        <div class="section-card">
          <div class="section-title">What users would say</div>
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
        <div class="section-card">
          <div class="section-title">Why Smart Job Finder AI matters</div>
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
    job_type = str(job.get("type", "")).lower()

    if "remote" in location or "remote" in job_type:
        tags.append('<span class="job-chip chip-remote">Remote</span>')
    if "ai" in title or "artificial intelligence" in title or "artificial intelligence" in skills:
        tags.append('<span class="job-chip chip-ai">AI</span>')
    if "ml" in title or "machine learning" in title or "machine learning" in skills:
        tags.append('<span class="job-chip chip-ml">ML</span>')

    tags.append(f'<span class="job-chip chip-score">Score {job["score"]}</span>')
    tags.append(f'<span class="job-chip">{job["source"]}</span>')
    return "".join(tags)


def _render_skill_tags(skills: list[str]) -> str:
    if not skills:
        return '<span class="skill-chip">No skill tags</span>'
    return "".join(f'<span class="skill-chip">{skill}</span>' for skill in skills[:6])


def _render_job_card(job: dict, index: int) -> None:
    st.markdown(
        f"""
        <div class="job-card">
          <div class="job-top">
            <div>
              <div class="job-title-main">{index}. {job['title']}</div>
              <div class="job-company-row"><span class="company-badge"></span>{job['company']}</div>
            </div>
            <div class="salary-pill">{job['salary']}</div>
          </div>
          <div class="job-meta">
            <span class="job-chip">{job['location']}</span>
            <span class="job-chip">{job['type']}</span>
            {_job_tags(job)}
          </div>
          <div class="skill-tag-row">
            {_render_skill_tags(job['skills'])}
          </div>
          <div class="job-description">A strong-fit opportunity surfaced by your AI ranking pipeline, ready to save, track, or apply.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([0.8, 3.2])
    with col1:
        st.link_button("Apply Now", job["link"], use_container_width=True)
    with col2:
        st.caption("Use the controls below to update application status and notes.")


def _render_resume_analysis(analysis: dict) -> None:
    st.markdown('<div id="resume-lab"></div>', unsafe_allow_html=True)
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
        if st.button("Find Jobs"):
            st.session_state.active_page = "Find Jobs"
            st.rerun()
    ranked_jobs = [_normalize_job(job) for job in st.session_state.ranked_jobs]
    profile = st.session_state.profile
    resume_analysis = st.session_state.resume_analysis
    tracked_applications = get_all_applications()
    global_query = _render_topbar_search()
    filtered_jobs = _filter_jobs_by_query(ranked_jobs, global_query)
    metrics = _derive_metrics(ranked_jobs, len(tracked_applications))

    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    left_col, right_col = st.columns([3.15, 1.2], gap="large")

    with left_col:
        _render_hero(metrics)

        page = st.session_state.get("active_page", "Landing")

        if page == "Landing":
            _render_feature_highlights(profile, ranked_jobs)
            _render_hiring_companies()
            _render_resume_cta()

            st.markdown(
                """
                <div class="section-card">
                  <div class="section-title">Product Overview</div>
                  <div class="feature-grid">
                    <div class="feature-card">
                      <div class="feature-kicker">Discover</div>
                      <div class="feature-title">AI-ranked job search</div>
                      <div class="feature-copy">Filter and rank opportunities based on profile fit instead of manually scanning noisy listings.</div>
                    </div>
                    <div class="feature-card">
                      <div class="feature-kicker">Improve</div>
                      <div class="feature-title">Resume intelligence</div>
                      <div class="feature-copy">Find weak phrasing, missing ATS keywords, and sharper rewrite suggestions for stronger shortlisting potential.</div>
                    </div>
                    <div class="feature-card">
                      <div class="feature-kicker">Track</div>
                      <div class="feature-title">Application tracker</div>
                      <div class="feature-copy">Move applications through stages, save notes, and keep your search organized with less friction.</div>
                    </div>
                    <div class="feature-card">
                      <div class="feature-kicker">Convert</div>
                      <div class="feature-title">Email studio</div>
                      <div class="feature-copy">Generate professional application and follow-up drafts from the same workspace where you discover roles.</div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            _render_blog_section()
            _render_testimonials()

        elif page == "Find Jobs":
            _render_feature_highlights(profile, ranked_jobs)
            st.markdown(
                """
                <div class="section-card">
                  <div class="section-title">Find Jobs</div>
                  <div class="section-copy">Explore ranked opportunities with premium cards, dynamic top search filtering, and quick application actions.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not ranked_jobs:
                st.info("Use the sidebar profile inputs and click Find Jobs to populate this workspace.")
            elif not filtered_jobs:
                st.warning("No jobs match your current search. Try a broader keyword like a skill, company, or role.")
            else:
                for index, job in enumerate(filtered_jobs[:10], start=1):
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
                <div class="section-card">
                  <div class="section-title">Resume Lab</div>
                  <div class="section-copy">Review ATS scoring, missing keywords, buzzword findings, and better rewrite suggestions.</div>
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
                <div class="section-card">
                  <div class="section-title">Application Tracker</div>
                  <div class="section-copy">Review your pipeline and filter applications by stage.</div>
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
                <div class="section-card">
                  <div class="section-title">Email Studio</div>
                  <div class="section-copy">Generate polished application and follow-up drafts for your selected role.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not ranked_jobs:
                st.info("Run a search first to generate email drafts.")
            else:
                selectable_jobs = filtered_jobs[:10] if filtered_jobs else ranked_jobs[:10]
                job_labels = [
                    f"{index + 1}. {job['title']} - {job['company']}"
                    for index, job in enumerate(selectable_jobs)
                ]
                selected_label = st.selectbox("Choose a job", options=job_labels)
                selected_index = job_labels.index(selected_label)
                selected_job = selectable_jobs[selected_index]

                draft_type = st.radio(
                    "Draft type",
                    options=["application", "followup"],
                    horizontal=True,
                )
                _render_email_draft(selected_job, profile, draft_type)

    with right_col:
        _render_news_panel()

    st.markdown(
        '<div class="footer-note">Premium AI career platform UI upgraded with dynamic search, insights, glow styling, and modular frontend sections.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
