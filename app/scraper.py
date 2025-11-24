import csv
import requests
from bs4 import BeautifulSoup
from email_utils import send_email
import os

# Get search term from environment variable or default to empty string
SEARCH_TERM = os.getenv("SEARCH_TERM", "")

def scrape_jobs_indeed(query=SEARCH_TERM, location="Watford, UK", radius=10):
    """Scrape Indeed for hybrid & remote jobs with minimum salary ~30k."""
    jobs = []

    base_url = "https://www.indeed.co.uk/jobs"
    params = {
        "q": query,
        "l": location,
        "radius": radius,
        "explvl": "entry_level",
        "fromage": "1",  # last 1 day
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(base_url, params=params, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all("div", class_="job_seen_beacon")

    for job in results:
        title = job.find("h2", class_="jobTitle")
        company = job.find("span", class_="companyName")
        location_tag = job.find("div", class_="companyLocation")
        salary_tag = job.find("span", class_="salary-snippet")
        link_tag = job.find("a", href=True)

        if not title or not link_tag:
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and ("30,000" not in salary_text and "£" in salary_text):
            continue

        jobs.append({
            "title": title.text.strip(),
            "company": company.text.strip() if company else "",
            "location": location_tag.text.strip() if location_tag else "",
            "salary": salary_text,
            "url": "https://www.indeed.co.uk" + link_tag["href"]
        })

    return jobs

def main():
    jobs = scrape_jobs_indeed()
    print(f"Found {len(jobs)} jobs")

    if jobs:
        keys = jobs[0].keys()
        with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, keys, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(jobs)

        send_email(
            subject=f"Daily Job Results for '{SEARCH_TERM or 'Any'}'",
            body=f"{len(jobs)} jobs found today. CSV attached.",
            attachment_path="jobs.csv"
        )
    else:
        # Send email even if no jobs found
        send_email(
            subject=f"Daily Job Results for '{SEARCH_TERM or 'Any'}'",
            body="No jobs found today matching your criteria.",
        )
        print("No jobs found today.")

if __name__ == "__main__":
    main()
