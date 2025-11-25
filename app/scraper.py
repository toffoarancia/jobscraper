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
            body=f"{len(all_jobs)} jobs found today. CSV attached.",
            attachment_path="jobs.csv",
        )

    else:
        send_email(
            subject=f"Daily Job Results for '{SE
