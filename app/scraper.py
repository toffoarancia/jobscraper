# app/scraper.py — diagnostic + robust runner
import sys
import os
import traceback
import time
import csv

# Make logs flush immediately so Actions shows them live
def log(*parts):
    print(*parts, flush=True)

log("=== START scraper.py ===")
log("Python:", sys.version.replace("\n", " "))
log("CWD:", os.getcwd())
log("Listing project files (top-level):")
for p in sorted(os.listdir(".")):
    log(" -", p)

# Try to import send_email and scrapers; capture errors and show stack traces
send_email = None
scrape_indeed = None
scrape_reed = None
scrape_cvlibrary = None

try:
    # import email util
    from email_utils import send_email as _send_email
    send_email = _send_email
    log("Imported email_utils.send_email OK")
except Exception:
    log("Failed to import email_utils.send_email:")
    traceback.print_exc()

# Attempt to import site scrapers (these modules should exist in app/)
try:
    # these modules are expected to be in the same package / folder (app/)
    from indeed_scraper import scrape_indeed as _indeed
    scrape_indeed = _indeed
    log("Imported indeed_scraper.scrape_indeed OK")
except Exception:
    log("Failed to import indeed_scraper.scrape_indeed:")
    traceback.print_exc()

try:
    from reed_scraper import scrape_reed as _reed
    scrape_reed = _reed
    log("Imported reed_scraper.scrape_reed OK")
except Exception:
    log("Failed to import reed_scraper.scrape_reed:")
    traceback.print_exc()

try:
    from cvlibrary_scraper import scrape_cvlibrary as _cv
    scrape_cvlibrary = _cv
    log("Imported cvlibrary_scraper.scrape_cvlibrary OK")
except Exception:
    log("Failed to import cvlibrary_scraper.scrape_cvlibrary:")
    traceback.print_exc()

# Provide a simple fallback scraper in case imports missing
def fallback_scraper(keyword, site_name):
    log(f"[fallback] Simulating {site_name} search for '{keyword}' — returning 0 results")
    return []

KEYWORDS = ["Customer", "IT", "Administrator"]

def run_all():
    all_jobs = []
    log("\n===== Scraping started =====\n")
    for kw in KEYWORDS:
        log(f"--- Keyword: {kw} ---")
        # indeed
        try:
            fn = scrape_indeed or (lambda k: fallback_scraper(k, "Indeed"))
            res = fn(kw)
            log(f"Indeed results for '{kw}': {len(res)}")
            all_jobs.extend(res or [])
        except Exception:
            log("Error scraping Indeed for", kw)
            traceback.print_exc()

        # reed
        try:
            fn = scrape_reed or (lambda k: fallback_scraper(k, "Reed"))
            res = fn(kw)
            log(f"Reed results for '{kw}': {len(res)}")
            all_jobs.extend(res or [])
        except Exception:
            log("Error scraping Reed for", kw)
            traceback.print_exc()

        # cv-library
        try:
            fn = scrape_cvlibrary or (lambda k: fallback_scraper(k, "CV-Library"))
            res = fn(kw)
            log(f"CV-Library results for '{kw}': {len(res)}")
            all_jobs.extend(res or [])
        except Exception:
            log("Error scraping CV-Library for", kw)
            traceback.print_exc()

        time.sleep(1)  # small pause between keywords

    log("\n===== Scraping finished =====")
    log("Total jobs found:", len(all_jobs))
    return all_jobs

def save_csv(jobs, filename="jobs.csv"):
    keys = ["site", "title", "company", "location", "salary", "url"]
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, keys, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for j in jobs:
                # write only expected keys; missing keys become empty
                row = {k: j.get(k, "") for k in keys}
                writer.writerow(row)
        log("Saved CSV:", filename)
        return filename
    except Exception:
        log("Failed to save CSV:")
        traceback.print_exc()
        return None

def ensure_send_email_available():
    global send_email
    if send_email is None:
        # create a debug send_email that just logs
        def debug_send_email(subject, body, attachment_path=None):
            log("[debug send_email] SUBJECT:", subject)
            log("[debug send_email] BODY:", body)
            log("[debug send_email] ATTACHMENT:", attachment_path)
            return True
        send_email = debug_send_email
        log("Using debug send_email (original import missing)")

def main():
    ensure_send_email_available()
    jobs = run_all()
    csv_file = save_csv(jobs) if jobs else None

    # Compose subject/body
    subject = "Daily Job Results: Customer / IT / Administrator"
    body = f"{len(jobs)} jobs found."

    log("About to call send_email(...)")
    try:
        send_email(subject, body, csv_file)
        log("send_email() completed")
    except Exception:
        log("send_email() raised exception:")
        traceback.print_exc()
        # don't re-raise: we still want workflow to finish and logs to show

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("Unhandled exception in main():")
        traceback.print_exc()
        # exit non-zero to mark failure
        sys.exit(1)
    finally:
        log("=== END scraper.py ===")
