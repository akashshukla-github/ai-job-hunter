from __future__ import annotations

from db import (
    get_all_applications,
    get_applications_by_status,
    init_db,
    print_applications,
    save_application,
    save_jobs,
    update_application_status,
)
from email_utils import (
    generate_application_email,
    generate_followup_email,
    print_email_draft,
)
from filter import aggregate_jobs, print_jobs
from resume import analyze_resume, load_resume_text, print_resume_analysis
from scraper import get_jobs


VALID_TRACKING_STATUSES = {
    "saved",
    "applied",
    "interview",
    "rejected",
    "offer",
    "follow_up",
}


def _parse_csv_input(prompt: str) -> list[str]:
    raw_value = input(prompt).strip()
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def get_user_profile() -> dict[str, list[str]]:
    return {
        "skills": _parse_csv_input("Enter your skills (comma separated): "),
        "preferred_roles": _parse_csv_input("Enter preferred roles: "),
        "locations": _parse_csv_input("Preferred locations (remote/city): "),
    }


def collect_all_jobs() -> list[dict]:
    all_jobs: list[dict] = []

    try:
        internshala_jobs = get_jobs()
        all_jobs.extend(internshala_jobs)
    except Exception as error:
        print(f"Failed to fetch Internshala jobs: {error}")

    return all_jobs


def display_top_jobs(jobs: list[dict], limit: int = 5) -> None:
    if not jobs:
        print("No relevant jobs found for the given profile.")
        return

    print("Top Matching Jobs")
    print("-----------------")
    print_jobs(jobs[:limit])


def track_job_applications(jobs: list[dict], limit: int = 5) -> None:
    if not jobs:
        return

    print("\nApplication Tracker")
    print("-------------------")
    print("Mark jobs as: saved, applied, interview, rejected, offer, follow_up")
    print("Press Enter to skip.\n")

    for index, job in enumerate(jobs[:limit], start=1):
        print(f"{index}. {job['title']} - {job['company']}")
        print(f"   Link: {job['link']}")

        status = input("   Enter status: ").strip().lower()
        if not status:
            print("   Skipped.\n")
            continue

        if status not in VALID_TRACKING_STATUSES:
            print("   Invalid status. Skipping.\n")
            continue

        notes = input("   Add notes (optional): ").strip()

        try:
            save_application(job["link"], status=status, notes=notes)
            print(f"   Status saved as '{status}'.\n")
        except ValueError as error:
            print(f"   Failed to save status: {error}\n")


def view_tracked_applications() -> None:
    choice = input("\nDo you want to view tracked applications? (y/n): ").strip().lower()
    if choice not in {"y", "yes"}:
        return

    status_filter = input(
        "Enter status filter (saved/applied/interview/rejected/offer/follow_up) or press Enter for all: "
    ).strip().lower()

    try:
        if not status_filter:
            applications = get_all_applications()
        elif status_filter in VALID_TRACKING_STATUSES:
            applications = get_applications_by_status(status_filter)
        else:
            print("Invalid status filter. Showing all applications instead.\n")
            applications = get_all_applications()

        print("\nTracked Applications")
        print("--------------------")
        print_applications(applications)
    except ValueError as error:
        print(f"Failed to load tracked applications: {error}")


def update_tracked_application_status() -> None:
    choice = input("\nDo you want to update any tracked application status? (y/n): ").strip().lower()
    if choice not in {"y", "yes"}:
        return

    applications = get_all_applications()
    if not applications:
        print("No tracked applications found to update.")
        return

    print("\nAvailable Tracked Applications")
    print("------------------------------")
    print_applications(applications)

    job_link = input("Enter the exact job link to update status: ").strip()
    if not job_link:
        print("Update skipped.")
        return

    status = input("Enter new status: ").strip().lower()
    if status not in VALID_TRACKING_STATUSES:
        print("Invalid status. Update skipped.")
        return

    notes = input("Add notes (optional): ").strip()

    try:
        update_application_status(job_link, status=status, notes=notes)
        print(f"Application status updated to '{status}'.")
    except ValueError as error:
        print(f"Failed to update application status: {error}")


def _read_multiline_resume_input() -> str:
    print("\nPaste your resume text below. Press Enter on an empty line to finish:")
    lines: list[str] = []

    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)

    return "\n".join(lines).strip()


def _get_resume_text() -> str:
    resume_input = input(
        "\nEnter resume file path (.txt or .md), type 'paste' to paste resume text, or press Enter to skip: "
    ).strip()

    if not resume_input:
        return ""

    if resume_input.lower() == "paste":
        return _read_multiline_resume_input()

    return load_resume_text(resume_input)


def run_resume_analysis(profile: dict[str, list[str]], top_jobs: list[dict]) -> None:
    if not top_jobs:
        print("\nResume analysis skipped: no matched jobs available for comparison.")
        return

    try:
        resume_text = _get_resume_text()
        if not resume_text:
            print("Resume analysis skipped.")
            return

        analysis = analyze_resume(resume_text, top_jobs, profile)

        print("\nResume Analysis")
        print("---------------")
        print_resume_analysis(analysis)
    except (FileNotFoundError, ValueError) as error:
        print(f"Resume analysis skipped: {error}")


def draft_emails_for_jobs(profile: dict[str, list[str]], jobs: list[dict], limit: int = 5) -> None:
    if not jobs:
        return

    choice = input("\nDo you want to generate an email draft? (y/n): ").strip().lower()
    if choice not in {"y", "yes"}:
        return

    print("\nAvailable Jobs For Email Drafting")
    print("---------------------------------")
    for index, job in enumerate(jobs[:limit], start=1):
        print(f"{index}. {job['title']} - {job['company']}")
        print(f"   Link: {job['link']}")

    selected = input("\nEnter job number to draft email for: ").strip()
    if not selected.isdigit():
        print("Invalid selection. Email drafting skipped.")
        return

    job_index = int(selected) - 1
    if job_index < 0 or job_index >= min(limit, len(jobs)):
        print("Invalid selection. Email drafting skipped.")
        return

    email_type = input("Enter email type (application/followup): ").strip().lower()
    if email_type not in {"application", "followup"}:
        print("Invalid email type. Email drafting skipped.")
        return

    selected_job = jobs[job_index]

    if email_type == "application":
        email_draft = generate_application_email(selected_job, profile)
    else:
        email_draft = generate_followup_email(selected_job, profile)

    print()
    print_email_draft(email_draft)


def main() -> None:
    print("AI Job Hunter")
    print("=============\n")

    init_db()

    profile = get_user_profile()
    all_jobs = collect_all_jobs()
    ranked_jobs = aggregate_jobs(all_jobs, profile, limit=20)

    if ranked_jobs:
        save_jobs(ranked_jobs)

    print(f"\nTotal jobs collected: {len(all_jobs)}")
    print(f"Relevant jobs found: {len(ranked_jobs)}\n")

    display_top_jobs(ranked_jobs, limit=5)

    if ranked_jobs:
        track_job_applications(ranked_jobs, limit=5)
        view_tracked_applications()
        update_tracked_application_status()
        draft_emails_for_jobs(profile, ranked_jobs, limit=5)
        run_resume_analysis(profile, ranked_jobs[:5])
    else:
        print("Skipping application tracking, email drafting, and resume analysis because no relevant jobs were found.")
        view_tracked_applications()
        update_tracked_application_status()


if __name__ == "__main__":
    main()
