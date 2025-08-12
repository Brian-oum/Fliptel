import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from Jobs.models import Job
from dateutil.parser import parse as parse_date
from html import unescape
from urllib.parse import urlparse, urljoin
import time

class Command(BaseCommand):
    help = 'Scrape all job opportunities from opportunitiesforyoungkenyans.co.ke'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('🔍 Starting job scraping from opportunitiesforyoungkenyans.co.ke...'))

        jobs = self.scrape_all_jobs()
        if not jobs:
            self.stdout.write(self.style.WARNING('⚠️ No jobs found on website, trying RSS feed...'))
            jobs = self.scrape_rss_feed()

        self.stdout.write(f"📌 Found {len(jobs)} jobs")

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

    def scrape_all_jobs(self):
        base_url = 'https://opportunitiesforyoungkenyans.co.ke'
        # Update this URL based on the correct job listing page
        start_url = f'{base_url}/category/job-opportunities/'  # Example: Adjust to actual URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        jobs = []

        current_page = 1
        while True:
            page_url = f'{start_url}page/{current_page}/' if current_page > 1 else start_url
            self.stdout.write(self.style.NOTICE(f"📄 Scraping page: {page_url}"))

            try:
                response = requests.get(page_url, headers=headers, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                job_listings = soup.select('article')  # Adjust selector based on website's HTML

                if not job_listings:
                    self.stdout.write(self.style.WARNING(f"⚠️ No jobs found on page {current_page}. Stopping."))
                    break

                self.stdout.write(self.style.NOTICE(f"📋 Found {len(job_listings)} job listings on page {current_page}"))

                for job_item in job_listings:
                    job = self.scrape_job_details(job_item, base_url, headers)
                    if job:
                        jobs.append(job)

                current_page += 1
                time.sleep(1)  # Be polite to the server

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"❌ Error fetching page {page_url}: {str(e)}"))
                break

        return jobs

    def scrape_rss_feed(self):
        url = 'https://opportunitiesforyoungkenyans.co.ke/feed/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        jobs = []

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'xml')
            listings = soup.find_all('item')

            self.stdout.write(self.style.NOTICE(f"📋 Found {len(listings)} items in RSS feed"))

            for item in listings:
                title = item.find('title').get_text(strip=True) if item.find('title') else 'No title'
                link = unescape(item.find('link').get_text(strip=True)) if item.find('link') else ''
                raw_description = item.find('description').get_text() if item.find('description') else ''

                description_soup = BeautifulSoup(raw_description, 'html.parser')
                description = description_soup.get_text(" ", strip=True)

                posted_date = timezone.now()
                if item.find('pubDate'):
                    try:
                        parsed_date = parse_date(item.find('pubDate').get_text(strip=True))
                        if not timezone.is_aware(parsed_date):
                            parsed_date = timezone.make_aware(parsed_date)
                        posted_date = parsed_date
                    except Exception:
                        self.stdout.write(self.style.WARNING(f"⚠️ Could not parse date for {title}"))

                company, location = self.extract_company_location(description)

                jobs.append({
                    'title': title,
                    'url': link,
                    'location': location,
                    'company': company,
                    'posted_date': posted_date,
                    'source': 'Opportunities for Young Kenyans (RSS)',
                    'description': description
                })

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Error fetching RSS feed: {str(e)}"))
            return []

        return jobs

    def scrape_job_details(self, job_item, base_url, headers):
        try:
            title_elem = job_item.select_one('h2.entry-title a')  # Adjust selector
            title = title_elem.get_text(strip=True) if title_elem else 'No title'
            job_url = urljoin(base_url, title_elem['href']) if title_elem and title_elem.get('href') else ''

            if not job_url:
                self.stdout.write(self.style.WARNING(f"⚠️ Skipping job with no URL: {title}"))
                return None

            response = requests.get(job_url, headers=headers, timeout=15)
            response.raise_for_status()
            job_soup = BeautifulSoup(response.text, 'html.parser')

            content_elem = job_soup.select_one('div.entry-content')  # Adjust selector
            description = content_elem.get_text(" ", strip=True) if content_elem else 'No description'

            posted_date = timezone.now()
            date_elem = job_soup.select_one('time.entry-date')  # Adjust selector
            if date_elem:
                try:
                    parsed_date = parse_date(date_elem.get_text(strip=True))
                    if not timezone.is_aware(parsed_date):
                        parsed_date = timezone.make_aware(parsed_date)
                    posted_date = parsed_date
                except Exception:
                    self.stdout.write(self.style.WARNING(f"⚠️ Could not parse date for {title}"))

            company, location = self.extract_company_location(description)

            return {
                'title': unescape(title),
                'url': job_url,
                'location': location,
                'company': company,
                'posted_date': posted_date,
                'source': 'Opportunities for Young Kenyans',
                'description': description
            }

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error scraping job {title}: {str(e)}"))
            return None

    def extract_company_location(self, description):
        company = 'Unknown'
        location = 'Unknown'

        parts = description.split('|')
        if len(parts) >= 2:
            company = parts[0].strip()
            location = parts[1].strip()
        else:
            if ' at ' in description:
                parts = description.split(' at ')
                company = parts[0].strip()
                location = parts[1].split()[0].strip() if len(parts) > 1 else 'Unknown'

        return company, location

    def normalize_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def is_duplicate(self, job):
        norm_url = self.normalize_url(job['url'])
        job_date = job['posted_date'].date()

        exists = Job.objects.filter(url=norm_url, posted_date__date=job_date).exists() \
                 or Job.objects.filter(title__iexact=job['title'], posted_date__date=job_date).exists()

        if exists:
            self.stdout.write(f"⏭️ Skipping duplicate: {job['title']}")
            return True
        return False