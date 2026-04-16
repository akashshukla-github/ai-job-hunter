from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jobs.db"

VALID_STATUSES = {
    "saved",
    "applied",
    "interview",
    "rejected",
    "offer",
    "follow_up",
}


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def init_db() -> None:
    with _get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                skills TEXT,
                link TEXT NOT NULL UNIQUE,
                source TEXT,
                salary TEXT DEFAULT 'N/A',
                score INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_link TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'saved',
                notes TEXT DEFAULT '',
                applied_at TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (job_link) REFERENCES jobs(link)
            )
            """
        )

        connection.commit()


def _normalize_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": job.get("title", "N/A"),
        "company": job.get("company", "N/A"),
        "location": job.get("location", "N/A"),
        "skills": json.dumps(job.get("skills", [])),
        "link": job.get("link", ""),
        "source": job.get("source", "unknown"),
        "salary": job.get("salary", "N/A"),
        "score": int(job.get("score", 0)),
    }


def save_job(job: dict[str, Any]) -> None:
    normalized = _normalize_job(job)
    if not normalized["link"]:
        return

    now = _utc_now()

    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (
                title, company, location, skills, link, source, salary, score, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(link) DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                skills = excluded.skills,
                source = excluded.source,
                salary = excluded.salary,
                score = excluded.score,
                updated_at = excluded.updated_at
            """,
            (
                normalized["title"],
                normalized["company"],
                normalized["location"],
                normalized["skills"],
                normalized["link"],
                normalized["source"],
                normalized["salary"],
                normalized["score"],
                now,
                now,
            ),
        )
        connection.commit()


def save_jobs(jobs: list[dict[str, Any]]) -> None:
    for job in jobs:
        save_job(job)


def get_all_jobs(limit: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT title, company, location, skills, link, source, salary, score, created_at, updated_at
        FROM jobs
        ORDER BY score DESC, updated_at DESC
    """
    params: tuple[Any, ...] = ()

    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)

    with _get_connection() as connection:
        cursor = connection.cursor()
        rows = cursor.execute(query, params).fetchall()

    return [_row_to_job_dict(row) for row in rows]


def get_job_by_link(job_link: str) -> dict[str, Any] | None:
    with _get_connection() as connection:
        cursor = connection.cursor()
        row = cursor.execute(
            """
            SELECT title, company, location, skills, link, source, salary, score, created_at, updated_at
            FROM jobs
            WHERE link = ?
            """,
            (job_link,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_job_dict(row)


def save_application(job_link: str, status: str = "saved", notes: str = "") -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    now = _utc_now()
    applied_at = now if status == "applied" else None

    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO applications (job_link, status, notes, applied_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(job_link) DO UPDATE SET
                status = excluded.status,
                notes = excluded.notes,
                applied_at = COALESCE(applications.applied_at, excluded.applied_at),
                updated_at = excluded.updated_at
            """,
            (job_link, status, notes, applied_at, now),
        )
        connection.commit()


def update_application_status(job_link: str, status: str, notes: str = "") -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    now = _utc_now()
    applied_at_value = now if status == "applied" else None

    with _get_connection() as connection:
        cursor = connection.cursor()
        existing = cursor.execute(
            "SELECT job_link, applied_at FROM applications WHERE job_link = ?",
            (job_link,),
        ).fetchone()

        if existing is None:
            cursor.execute(
                """
                INSERT INTO applications (job_link, status, notes, applied_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_link, status, notes, applied_at_value, now),
            )
        else:
            cursor.execute(
                """
                UPDATE applications
                SET status = ?,
                    notes = ?,
                    applied_at = COALESCE(applied_at, ?),
                    updated_at = ?
                WHERE job_link = ?
                """,
                (status, notes, applied_at_value, now, job_link),
            )

        connection.commit()


def get_application(job_link: str) -> dict[str, Any] | None:
    with _get_connection() as connection:
        cursor = connection.cursor()
        row = cursor.execute(
            """
            SELECT id, job_link, status, notes, applied_at, updated_at
            FROM applications
            WHERE job_link = ?
            """,
            (job_link,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def get_all_applications() -> list[dict[str, Any]]:
    with _get_connection() as connection:
        cursor = connection.cursor()
        rows = cursor.execute(
            """
            SELECT a.id, a.job_link, a.status, a.notes, a.applied_at, a.updated_at,
                   j.title, j.company, j.location, j.source, j.salary, j.score
            FROM applications a
            LEFT JOIN jobs j ON a.job_link = j.link
            ORDER BY a.updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_applications_by_status(status: str) -> list[dict[str, Any]]:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    with _get_connection() as connection:
        cursor = connection.cursor()
        rows = cursor.execute(
            """
            SELECT a.id, a.job_link, a.status, a.notes, a.applied_at, a.updated_at,
                   j.title, j.company, j.location, j.source, j.salary, j.score
            FROM applications a
            LEFT JOIN jobs j ON a.job_link = j.link
            WHERE a.status = ?
            ORDER BY a.updated_at DESC
            """,
            (status,),
        ).fetchall()

    return [dict(row) for row in rows]


def delete_job(job_link: str) -> None:
    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM applications WHERE job_link = ?", (job_link,))
        cursor.execute("DELETE FROM jobs WHERE link = ?", (job_link,))
        connection.commit()


def _row_to_job_dict(row: sqlite3.Row) -> dict[str, Any]:
    skills = []
    try:
        skills = json.loads(row["skills"]) if row["skills"] else []
    except json.JSONDecodeError:
        skills = []

    return {
        "title": row["title"],
        "company": row["company"],
        "location": row["location"],
        "skills": skills,
        "link": row["link"],
        "source": row["source"],
        "salary": row["salary"],
        "score": row["score"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def print_applications(applications: list[dict[str, Any]]) -> None:
    if not applications:
        print("No tracked applications found.")
        return

    for index, app in enumerate(applications, start=1):
        print(f"{index}. {app.get('title', 'N/A')} - {app.get('company', 'N/A')}")
        print(f"   Status: {app.get('status', 'N/A')}")
        print(f"   Location: {app.get('location', 'N/A')}")
        print(f"   Source: {app.get('source', 'N/A')}")
        print(f"   Score: {app.get('score', 'N/A')}")
        print(f"   Notes: {app.get('notes', '') or 'N/A'}")
        print(f"   Applied At: {app.get('applied_at', 'N/A') or 'N/A'}")
        print(f"   Updated At: {app.get('updated_at', 'N/A')}")
        print(f"   Link: {app.get('job_link', 'N/A')}")
        print()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")
