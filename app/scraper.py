import csv
import os
from jobspy import scrape_jobs
from email_utils import send_email

def main():
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "google"],
        search_term="software engineer",
        location="Watford, United Kingdom",
        linkedin_fetch_description=True,
        radius_miles=10,
        is_remote=True,
        min_salary=30000,
        results_wanted=50,
        hours_old=24,
        country_indeed='UK'
    )

    print(f"Found {len(jobs)} jobs")

    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

    body = f"{len(jobs)} jobs found today. CSV file attached."

    send_email(
        subject="Daily Job Results",
        body=body,
        attachment_path="jobs.csv"
    )


if __name__ == "__main__":
    main()
