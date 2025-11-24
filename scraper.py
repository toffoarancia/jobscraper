import csv
from jobspy import scrape_jobs
from email_utils import send_email

# Filters:
# - Hybrid roles within 10 miles of Watford (UK)
# - Remote roles paying >= £30,000

def main():
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "google"],
        search_term="software engineer",
        location="Watford, United Kingdom",
        linkedin_fetch_description=True,
        radius_miles=10,
        is_remote=True,  # also fetch remote jobs
        min_salary=30000,
        results_wanted=50,
        hours_old=24,
        country_indeed='UK'
    )

    print(f"Found {len(jobs)} jobs")
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

    if len(jobs) == 0:
        body = "No new hybrid/remote jobs found today."
    else:
        body = f"{len(jobs)} jobs found. CSV attached."

    send_email(
        subject="Daily Job Results",
        body=body,
        attachment_path="jobs.csv"
    )


if __name__ == "__main__":
    main()
