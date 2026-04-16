from scraper import get_jobs
def get_user_profile():
    skills = input("Enter your skills (comma separated): ").lower().split(",")
    roles = input("Enter preferred roles: ").lower().split(",")
    locations = input("Preferred locations (remote/city): ").lower().split(",")

    return {
    "skills": [s.strip() for s in skills if s.strip()],
    "preferred_roles": [r.strip() for r in roles if r.strip()],
    "locations": [l.strip() for l in locations if l.strip()]
}
if __name__ == "__main__":
    user_profile = get_user_profile()
    print("\nUser Profile:", user_profile)

    jobs = get_jobs()
    print(f"\nTotal jobs fetched: {len(jobs)}")