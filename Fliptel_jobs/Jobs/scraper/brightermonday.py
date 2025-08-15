import requests
from bs4 import BeautifulSoup
import time

def scrape_brightermonday():
    jobs = []
    base_url = 'https://www.brightermonday.co.ke'
    list_url = f'{base_url}/jobs'
    try:
        response = requests.get(list_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # From recent structure: job listings in div.job-listing
        job_cards = soup.find_all('div', class_='job-listing')[:10]  # Limit to 10
        for card in job_cards:
            title_tag = card.find('h3', class_='job-title')
            link_tag = title_tag.find('a') if title_tag else None
            if not link_tag:
                continue
            job = {
                'title': title_tag.text.strip(),
                'link': base_url + link_tag['href'],
                'source': 'BrighterMonday'
            }
            company_tag = card.find('p', class_='company')
            job['company'] = company_tag.text.strip() if company_tag else None
            location_tag = card.find('p', class_='location')
            job['location'] = location_tag.text.strip() if location_tag else 'Kenya'
            desc_tag = card.find('p', class_='description')
            job['description'] = desc_tag.text.strip() if desc_tag else None
            # If description short, scrape details page
            if not job['description'] or len(job['description']) < 100:
                try:
                    detail_resp = requests.get(job['link'], timeout=10)
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    desc_div = detail_soup.find('div', class_='job-description')  # Adjust selector
                    job['description'] = desc_div.text.strip()[:2000] if desc_div else None
                except Exception as e:
                    print(f"Error scraping {job['link']}: {e}")
            jobs.append(job)
            time.sleep(1)
    except Exception as e:
        print(f"Error scraping BrighterMonday list: {e}")
    return jobs