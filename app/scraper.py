import csv
import requests
from bs4 import BeautifulSoup
from email_utils import send_email
import os

# Keywords to match
KEYWORDS = ["customer", "it", "administrator"]

# Get search term from environment variable
SEARCH_TERM = os.getenv("SEARCH_TERM", "").strip()
if SEARCH_TERM.upper() == "ALL" or SEARCH_TERM == "":
    SEARCH_TERM = ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------------------------------------------------------
# Helper: Keyword filter & salary filter
# -------------------------------------------------------

def matches_keywords(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def meets_salary(salary_text):
    if not salary_text:
        return False
    salary_text = salary_text.replace(",", "").replace("£", "")
    numbers = [int(s) for s in salary_text.split() if s.isdigit()]
    return any(n >= 30000 for n in numbers)


# -------------------------------------------------------
# INDEED SCRAPER
# -------------------------------------------------------

def scrape_jobs_indeed(query=SEARCH_TERM, location="Watford", radius=10):
    jobs = []

    base_url = "https://www.indeed.co.uk/jobs"
    params = {
        "q": query,
        "l": location,
        "radius": radius,
        "fromage": "1",
    }

    r = requests.get(base_url, params=params, headers=HEADERS)
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

        title_text = title.text.strip()

        # Keyword filter
        if not matches_keywords(title_text):
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        # Remote / hybrid check
        location_text = location_tag.text.lower() if location_tag else ""
        if not any(x in location_text for x in ["remote", "hybrid"]):
            continue

        jobs.append({
            "site": "Indeed",
            "title": title_text,
            "company": company.text.strip() if company else "",
            "location": location_text,
            "salary": salary_text,
            "url": "https://www.indeed.co.uk" + link_tag["href"]
        })

    return jobs


# -------------------------------------------------------
# REED SCRAPER
# -------------------------------------------------------

def scrape_jobs_reed(query=SEARCH_TERM):
    jobs = []

    url = (
        "https://www.reed.co.uk/jobs"
        f"?keywords={query}"
        "&location=Watford"
        "&proximity=10"
        "&datecreatedoffset=1"
    )

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all("article", class_="job-result")

    for job in results:
        title_tag = job.find("h3")
        company_tag = job.find("a", class_="gtmJobListingPostedBy")
        location_tag = job.find("li", class_="location")
        salary_tag = job.find("li", class_="salary")
        link_tag = title_tag.find("a") if title_tag else None

        if not title_tag or not link_tag:
            continue

        title = title_tag.text.strip()

        # Keyword filter
        if not matches_keywords(title):
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        location_text = location_tag.text.lower() if location_tag else ""
        if not any(x in location_text for x in ["remote", "hybrid"]):
            continue

        jobs.append({
            "site": "Reed",
            "title": title,
            "company": company_tag.text.strip() if company_tag else "",
            "location": location_text,
            "salary": salary_text,
            "url": "https://www.reed.co.uk" + link_tag["href"]
        })

    return jobs


# -------------------------------------------------------
# CV-LIBRARY SCRAPER
# -------------------------------------------------------

def scrape_jobs_cvlibrary(query=SEARCH_TERM):
    jobs = []

    url = (
        "https://www.cv-library.co.uk/search-jobs"
        f"?distance=10&keywords={query}&location=Watford"
    )

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all("article", class_="job")

    for job in results:
        title_tag = job.find("h2", class_="title")
        company_tag = job.find("a", class_="company")
        location_tag = job.find("span", class_="location")
        salary_tag = job.find("li", class_="salary")
        link_tag = title_tag.find("a") if title_tag else None

        if not title_tag or not link_tag:
            continue

        title = title_tag.text.strip()

        # Keyword filter
        if not matches_keywords(title):
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        location_text = location_tag.text.lower() if location_tag else ""
        if not any(x in location_text for x in ["remote", "hybrid"]):
            continue

        jobs.append({
            "site": "CV-Library",
            "title": title,
            "company": company_tag.text.strip() if company_tag else "",
            "location": location_text,
            "salary": salary_text,
            "url": "https://www.cv-library.co.uk" + link_tag["href"]
        })

    return jobs


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():
    all_jobs = []

    print("Scraping Indeed...")
    all_jobs.extend(scrape_jobs_indeed())

    print("Scraping Reed...")
    all_jobs.extend(scrape_jobs_reed())

    print("Scraping CV-Library...")
    all_jobs.extend(scrape_jobs_cvlibrary())

    print(f"Total jobs found: {len(all_jobs)}")

    if all_jobs:
        keys = all_jobs[0].keys()
        with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, keys, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(all_jobs)

        send_email(
            subject=f"Daily Job Results for '{SEARCH_TERM or 'ALL'}'",
