# Job Scraper

This repo scrapes hybrid and remote software engineer jobs in the UK and emails the results daily.

## Setup

1. Add GitHub Secrets:
   - `FROM_EMAIL` → your Gmail
   - `FROM_PASSWORD` → Gmail App Password
   - `TO_EMAIL` → recipient email

2. Push the repo to GitHub

3. GitHub Actions will automatically run the scraper daily at 08:00 UTC
