# Smart Job Finder AI

> Intelligent job discovery, resume optimization, application tracking, and recruiter outreach in one AI-powered workflow.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-8A5CF6)

---

## Overview

Job hunting is fragmented.

Candidates jump between platforms, scroll through irrelevant listings, manually compare roles, rewrite resumes for ATS systems, track applications in spreadsheets, and draft outreach emails from scratch. The result is wasted time, inconsistent execution, and lower response rates.

**Smart Job Finder AI** solves this by turning job search into a focused, intelligent workflow.

It combines job scraping, AI-assisted filtering and ranking, resume analysis, application tracking, and recruiter email generation into a single product experience. Instead of applying blindly, users can prioritize high-fit roles, improve their resume against those roles, track progress, and move faster with better signal.

---

## ✨ Features

### AI Job Matching
- Matches jobs against user-defined skills, preferred roles, and location preferences
- Expands related keywords intelligently for better relevance
- Helps surface stronger-fit opportunities instead of generic listings

### Smart Filtering & Ranking
- Scores jobs based on role match, skill match, and overall relevance
- Prioritizes the most actionable roles first
- Supports a normalized ranking pipeline for better decision-making

### Resume Analysis
- ATS-style resume scoring
- Keyword extraction and missing-skill detection
- Buzzword identification and rewrite suggestions
- Resume improvement guidance aligned with top-matched jobs

### Application Tracking
- Save and track opportunities across stages
- Status management for:
  - `saved`
  - `applied`
  - `interview`
  - `rejected`
  - `offer`
  - `follow_up`
- SQLite-backed persistence for lightweight local reliability

### AI Email Generation
- Generate polished application emails
- Generate follow-up emails for recruiters or hiring teams
- Uses role, company, and profile context for more relevant messaging

### Extensible Source Architecture
- Internshala integration is live
- Designed for future expansion to:
  - LinkedIn
  - Naukri
  - Indeed
  - company career pages
  - ATS sources such as Greenhouse and Lever

---

## 🖼 Demo / Screenshots

> Replace these placeholders with actual product screenshots.

![Landing Page](assets/landing.png)
![Job Finder](assets/jobs.png)
![Resume Lab](assets/resume.png)
![Application Tracker](assets/tracker.png)
![Email Studio](assets/email.png)

---

## 🛠 Tech Stack

**Core**
- Python
- Streamlit

**Data & Scraping**
- Requests
- BeautifulSoup

**Storage**
- SQLite

**Product Layer**
- Resume scoring and keyword analysis
- Rule-based job ranking engine
- Application tracking workflow
- Email draft generation

**Frontend**
- Streamlit UI
- Custom CSS
- Responsive glassmorphism-inspired design system

---

## 🏗 Architecture

Smart Job Finder AI is structured as a modular application with a clear separation between product logic and presentation.

### Frontend
`frontend/`
- Streamlit-based product interface
- Dashboard, landing page, job finder, resume lab, tracker, and email drafting views
- Custom styling for premium SaaS-like UX

### Backend
`backend/`
- `scraper.py` — job scraping logic
- `filter.py` — filtering, keyword expansion, scoring, ranking
- `resume.py` — ATS scoring, keyword extraction, rewrite suggestions
- `db.py` — SQLite persistence for jobs and applications
- `email_utils.py` — application and follow-up email generation
- `main.py` — CLI workflow and orchestration

### Data
`data/`
- SQLite database and job/application records

### High-Level Flow

```text
User Input
   ↓
Profile + Resume Context
   ↓
Job Scraper
   ↓
Filtering + Scoring Engine
   ↓
Ranked Jobs
   ↓
Resume Analysis + Tracking + Email Drafting
   ↓
Streamlit UI
