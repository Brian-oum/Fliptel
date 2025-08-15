import feedparser
import requests
from bs4 import BeautifulSoup
import time

def scrape_myjobmag():
    jobs = []
    feed_url = 'https://www.myjobmag.co.ke/jobs-rss'  # Confirmed RSS for jobs
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:10]:
        job = {
            'title': entry.title,
            'link': entry.link,
            'source': 'MyJobMag'
        }
        # Scrape details for company, location, description
        try:
            response = requests.get(entry.link, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Adjust selectors: e.g., company in span.job-company
            company_tag = soup.find('span', class_='job-company')
            job['company'] = company_tag.text.strip() if company_tag else None
            location_tag = soup.find('span', class_='job-location')
            job['location'] = location_tag.text.strip() if location_tag else 'Kenya'
            desc_div = soup.find('div', class_='job-description')
            job['description'] = desc_div.text.strip()[:2000] if desc_div else entry.summary
        except Exception as e:
            print(f"Error scraping {entry.link}: {e}")
            job['description'] = entry.summary
        jobs.append(job)
        time.sleep(1)
    return jobs