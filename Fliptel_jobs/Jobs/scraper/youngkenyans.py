import feedparser
import requests
from bs4 import BeautifulSoup
import time
import webbrowser

# SETTINGS
BASE_URL = "https://opportunitiesforyoungkenyans.co.ke"
AUTO_OPEN_LINKS = False  # Set to True to auto-open in browser

def scrape_youngkenyans():
    jobs = []

    # 1️⃣ Try RSS feed first
    feed_url = f"{BASE_URL}/feed/"
    feed = feedparser.parse(feed_url)

    if feed.entries:
        print("[INFO] Pulling job links from RSS feed...\n")
        job_links = [entry.link for entry in feed.entries[:10]]
        for link in job_links:
            print(f"[RSS] Found job link: {link}")
            if AUTO_OPEN_LINKS:
                webbrowser.open(link)
    else:
        print("[WARN] RSS failed. Falling back to HTML scraping...\n")
        job_links = scrape_links_from_html()

    # 2️⃣ Visit each job link and scrape details
    for link in job_links:
        job = {
            'title': None,
            'link': link,
            'source': 'YoungKenyans'
        }
        try:
            print(f"\n[SCRAPING] Visiting: {link}")
            response = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Title
            title_tag = soup.find('h1', class_='entry-title')
            job['title'] = title_tag.text.strip() if title_tag else "Untitled"

            # Description
            content = soup.find('div', class_='entry-content')
            job['description'] = content.get_text(separator="\n").strip()[:2000] if content else "No description found"

            # Company
            company_tag = soup.find('strong', string=lambda t: t and "Company" in t)
            job['company'] = company_tag.next_sibling.strip() if company_tag else "Not specified"

            # Location
            location_tag = soup.find('strong', string=lambda t: t and "Location" in t)
            job['location'] = location_tag.next_sibling.strip() if location_tag else "Kenya"

        except Exception as e:
            print(f"[ERROR] Could not scrape {link}: {e}")
            job['description'] = "Error fetching job details"

        jobs.append(job)
        time.sleep(1)  # Polite delay

    return jobs


def scrape_links_from_html():
    """Fallback: scrape job links from homepage/listing page"""
    job_links = []
    try:
        response = requests.get(BASE_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for a in soup.select('h2.entry-title a'):
            href = a.get('href')
            if href and href.startswith("http"):
                print(f"[HTML] Found job link: {href}")
                job_links.append(href)
                if AUTO_OPEN_LINKS:
                    webbrowser.open(href)

    except Exception as e:
        print(f"[ERROR] Failed to scrape HTML job links: {e}")
    return job_links


if __name__ == "__main__":
    all_jobs = scrape_youngkenyans()
    print("\n===== SCRAPED JOBS =====")
    for job in all_jobs:
        print(f"\nTitle: {job['title']}")
        print(f"Link: {job['link']}")  # Clickable in most terminals
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
