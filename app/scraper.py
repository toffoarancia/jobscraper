import time
import csv
from email_utils import send_email

from indeed_scraper import scrape_indeed
from reed_scraper import scrape_reed
from cvlibrary_scraper import scrape_cvlibrary

KEYWORDS = ["Customer", "IT", "Administrator"]


def scrape_all():
    all_jobs = []

    print("\n===== Job Scraper Started =====\n")

    for kw in KEYWORDS:
        print(f"\n🔍 Searching for keyword: {kw}")

        try:
            indeed = scrape_indeed(kw)
            print(f"Indeed returned {len(indeed)} jobs.")
            all_jobs.extend(indeed)
        except Exception as e:
            print(f"ERROR scraping Indeed for '{kw}': {e}")

        try:
            reed = scrape_reed(kw)
            print(f"Reed returned {len(reed)} jobs.")
            all_jobs.extend(reed)
        except Exception as e:
            print(f"ERROR scraping Reed for '{kw}': {e}")

        try:
            cv = scrape_cvlibrary(kw)
            print(f"CV-Library returned {len(cv)} jobs.")
            all_jobs.extend(cv)
        except Exception as e:
            print(f"ERROR scraping CV-Library for '{kw}': {e}")

        # Light delay to avoid rate limiting
        time.sleep(1)

    print(f"\n===== TOTAL JOB
