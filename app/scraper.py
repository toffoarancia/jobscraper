import os
import sys
import time
import csv
import traceback

# Ensure "app" folder is importable when running in GitHub Actions
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)

from email_utils import send_email
from indeed_scraper import scrape_indeed
from reed_scraper import scrape_reed
from cvlibrary_scraper import scrape_cvlibrary

KEYWORDS = ["Customer", "IT", "Administrator"]


def log(msg):
    print(msg, flush=True)


def scrape_all():
    all_jobs = []

    log("\n===== Job Scraper Started =====\n")

    for kw in KEYWORDS:
        log(f"\n🔍 Searching for keyword: {kw}")

        # --- Indeed ---
        try:
            indeed = scrape_indeed(kw)
            log(f"Indeed returned {len(indeed)} jobs.")
            all_jobs.extend(indeed)
        except Exception as e:
            log(f"❌ ERROR scraping Indeed for '{kw}': {e}")
            traceback.print_exc()

        # --- Reed ---
        try:
            reed = scrape_reed(kw)
            log(f"Reed returned {len(reed)} jobs.")
            all_jobs.extend(reed)
        except Exception as e:
            log(f"❌ ERROR scraping Reed for '{kw}': {e}")
            traceback.print_exc()

        # --- CV Library ---
        try:
            cv = scrape_cvlibrary(kw)
            log(f"CV-Library returned {len(cv)} jobs.")
            all_jobs.extend(cv)
        except Exception as e:
            log(f"❌ ERROR scraping CV-Library for '{kw}': {e}")
            traceback.print_exc()

        # Avoid rate limiting
        time.sleep(1)

    log(f"\n===== TOTAL JOBS COLLECTED: {len(all_jobs)} =====")
    return all_jobs


def save_csv(jobs):
    """Save results to jobs.csv"""
    if not jobs:
        log("⚠ No jobs found — skipping CSV save.")
        return None

    filename = "jobs.csv"
    keys = jobs[0].keys()

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, keys)
            writer.writeheader()
            writer.writerows(jobs)

        log(f"📄 Saved CSV: {filename}")
        return filename

    except Exception as e:
        log(f"❌ Error saving CSV: {e}")
        traceback.print_exc()
        return None


def main():
    jobs = scrape_all()
    csv_path = save_csv(jobs)

    log("\n📧 Sending email...")

    try:
        send_email(
            subject="Daily Job Results",
            body=f"{len(jobs)} job(s) found.\nSee attached CSV.",
            attachment_path=csv_path
        )
        log("✅ Email sent successfully!")
    except Exception as e:
        log(f"❌ Email sending failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
