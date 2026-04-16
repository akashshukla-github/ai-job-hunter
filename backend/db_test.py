from db import get_all_jobs, get_all_applications, print_applications

jobs = get_all_jobs(limit=5)
print("Saved jobs:", len(jobs))
for job in jobs:
    print(job["title"], "-", job["company"], "-", job["score"])

print("\nTracked applications:")
applications = get_all_applications()
print_applications(applications)
