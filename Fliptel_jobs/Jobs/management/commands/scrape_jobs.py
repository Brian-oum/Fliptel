import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from Jobs.models import Job
from dateutil.parser import parse as parse_date
from html import unescape
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Scrape job opportunities from opportunitiesforyoungkenyans.co.ke RSS feed'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('🔍 Starting job scraping...'))

        jobs = self.scrape_opportunities()
        self.stdout.write(f"📌 Found {len(jobs)} jobs in feed")

        saved_jobs = 0
        skipped_jobs = 0

        for job in jobs:
            if self.is_duplicate(job):
                skipped_jobs += 1
                continue

            try:
                Job.objects.create(
                    title=job['title'][:255],
                    url=self.normalize_url(job['url']),
                    location=job['location'][:255],
                    company=job['company'][:255],
                    posted_date=job['posted_date'],
                    source=job['source'],
                    description=job['description']
                )
                saved_jobs += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Saved job: {job['title']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error saving job {job['title']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            f"🎯 Finished scraping — {saved_jobs} new jobs saved, {skipped_jobs} duplicates skipped."
        ))

    def scrape_opportunities(self):
        url = 'https://opportunitiesforyoungkenyans.co.ke/feed/'
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'xml')
            listings = soup.find_all('item')

            jobs = []
            for item in listings:
                title = item.find('title').get_text(strip=True) if item.find('title') else 'No title'
                link = unescape(item.find('link').get_text(strip=True)) if item.find('link') else ''
                raw_description = item.find('description').get_text() if item.find('description') else ''

                # Clean HTML from description
                description_soup = BeautifulSoup(raw_description, 'html.parser')
                description = description_soup.get_text(" ", strip=True)

                # Extract posted date
                posted_date = timezone.now()
                if item.find('pubDate'):
                    try:
                        parsed_date = parse_date(item.find('pubDate').get_text(strip=True))
                        if not timezone.is_aware(parsed_date):
                            parsed_date = timezone.make_aware(parsed_date)
                        posted_date = parsed_date
                    except Exception:
                        self.stdout.write(self.style.WARNING(f"⚠️ Could not parse date for {title}"))

                # Extract company and location from description format: "Company | Location | Date"
                company, location = self.extract_company_location(description)

                jobs.append({
                    'title': title,
                    'url': link,
                    'location': location,
                    'company': company,
                    'posted_date': posted_date,
                    'source': 'Opportunities for Young Kenyans',
                    'description': description
                })

            return jobs

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Error fetching feed: {str(e)}"))
            return []

    def extract_company_location(self, description):
        company = 'Unknown'
        location = 'Unknown'

        # Many posts start with "Company | Location | Date"
        parts = description.split('|')
        if len(parts) >= 2:
            company = parts[0].strip()
            location = parts[1].strip()

        return company, location

    def normalize_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def is_duplicate(self, job):
        """
        Check if a job is a duplicate based on:
        1. Same normalized URL + same posted date
        2. Same title (case-insensitive) + same posted date
        """
        norm_url = self.normalize_url(job['url'])
        job_date = job['posted_date'].date()

        exists = Job.objects.filter(url=norm_url, posted_date__date=job_date).exists() \
                 or Job.objects.filter(title__iexact=job['title'], posted_date__date=job_date).exists()

        if exists:
            self.stdout.write(f"⏭️ Skipping duplicate: {job['title']}")
            return True
        return False
