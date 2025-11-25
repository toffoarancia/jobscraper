import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from email_utils import send_email
import urllib3

# -------------------------------------------------------
# Disable SSL warnings (for CV-Library)
# -------------------------------------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------------------------------
# Keywords
# -------------------------------------------------------
KEYWORDS = ["Customer", "IT", "Administrator"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------------------------------------------------------
# Helper functions
# -------------------------------------------------------
def meets_salary(salary_text):
    if not salary_text:
        return False
    salary_text = salary_text.replace(",", "").replace("£", "")
    numbers = [int(s) for s in salary_text.split() if s.isdigit()]
    return any(n >= 30000 for n in numbers)

def is_remote(location_text):
    if not location_text:
        return False
    location_text = location_text.lower()
    return "remote" in location_text or "hybrid" in location_text

# -------------------------------------------------------
# Async request helper
# -------------------------------------------------------
async def fetch(session, url, ssl_verify=True):
    try:
        async with session.get(url, ssl=ssl_verify, timeout=20) as response:
            return await response.text()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return ""

# -------------------------------------------------------
# Scrapers
# -------------------------------------------------------
async def scrape_jobs_indeed(session):
    jobs = []
    query = "Customer OR IT OR Administrator"
    url = "https://www.indeed.co.uk/jobs"
    params = {"q": query, "l": "Watford", "radius": 10, "fromage": "1"}

    text = await fetch(session, url + "?" + "&".join(f"{k}={v}" for k, v in params.items()))
    soup = BeautifulSoup(text, "html.parser")
    results = soup.find_all("div", class_="job_seen_beacon")

    for job in results:
        title_tag = job.find("h2", class_="jobTitle")
        company_tag = job.find("span", class_="companyName")
        location_tag = job.find("div", class_="companyLocation")
        salary_tag = job.find("span", class_="salary-snippet")
        link_tag = job.find("a", href=True)

        if not title_tag or not link_tag:
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        loc_text = location_tag.text if location_tag else ""
        if not is_remote(loc_text):
            continue

        jobs.append({
            "site": "Indeed",
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip() if company_tag else "",
            "location": loc_text,
            "salary": salary_text,
            "url": "https://www.indeed.co.uk" + link_tag["href"]
        })
    return jobs

async def scrape_jobs_reed(session):
    jobs = []
    query = "Customer OR IT OR Administrator"
    url = f"https://www.reed.co.uk/jobs?keywords={query}&location=Watford&proximity=10&datecreatedoffset=1"

    text = await fetch(session, url)
    soup = BeautifulSoup(text, "html.parser")
    results = soup.find_all("article", class_="job-result")

    for job in results:
        title_tag = job.find("h3")
        link_tag = title_tag.find("a") if title_tag else None
        company_tag = job.find("a", class_="gtmJobListingPostedBy")
        location_tag = job.find("li", class_="location")
        salary_tag = job.find("li", class_="salary")

        if not title_tag or not link_tag:
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        loc_text = location_tag.text if location_tag else ""
        if not is_remote(loc_text):
            continue

        jobs.append({
            "site": "Reed",
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip() if company_tag else "",
            "location": loc_text,
            "salary": salary_text,
            "url": "https://www.reed.co.uk" + link_tag["href"]
        })
    return jobs

async def scrape_jobs_cvlibrary(session):
    jobs = []
    query = "Customer+OR+IT+OR+Administrator"
    url = f"https://www.cv-library.co.uk/search-jobs?distance=10&keywords={query}&location=Watford"

    text = await fetch(session, url, ssl_verify=False)
    soup = BeautifulSoup(text, "html.parser")
    results = soup.find_all("article", class_="job")

    for job in results:
        title_tag = job.find("h2", class_="title")
        link_tag = title_tag.find("a") if title_tag else None
        company_tag = job.find("a", class_="company")
        location_tag = job.find("span", class_="location")
        salary_tag = job.find("li", class_="salary")

        if not title_tag or not link_tag:
            continue

        salary_text = salary_tag.text.strip() if salary_tag else ""
        if salary_text and not meets_salary(salary_text):
            continue

        loc_text = location_tag.text if location_tag else ""
        if not is_remote(loc_text):
            continue

        jobs.append({
            "site": "CV-Library",
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip() if company_tag else "",
            "location": loc_text,
            "salary": salary_text,
            "url": "https://www.cv-library.co.uk" + link_tag["href"]
        })
    return jobs

# -------------------------------------------------------
# Main async
# -------------------------------------------------------
async def main():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        indeed_task = scrape_jobs_indeed(session)
        reed_task = scrape_jobs_reed(session)
        cv_task = scrape_jobs_cvlibrary(session)

        results = await asyncio.gather(indeed_task, reed_task, cv_task)
        all_jobs = [job for sublist in results for job in sublist]

    print(f"Total jobs found: {len(all_jobs)}")

    if all_jobs:
        keys = ["site", "title", "company", "location", "salary", "url"]
        with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, keys, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(all_jobs)

        send_email(
            subject="Daily Job Results: Customer / IT / Administrator",
            body=f"{len(all_jobs)} jobs found today. CSV attached.",
            attachment_path="jobs.csv",
        )
    else:
        send_email(
            subject="Daily Job Results: Customer / IT / Administrator",
            body="No jobs found today matching your criteria.",
        )
        print("No jobs found today.")

# -------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
