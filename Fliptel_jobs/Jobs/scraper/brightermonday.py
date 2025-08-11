import requests
from bs4 import BeautifulSoup

def scrape_brightermonday_jobs():
    url = "https://www.brightermonday.co.ke/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    # This selector depends on the site HTML structure — update if needed!
    job_cards = soup.find_all('div', class_='job-card')  # example selector

    for card in job_cards:
        title_tag = card.find('h2')
        company_tag = card.find('div', class_='company-name')
        location_tag = card.find('div', class_='location')
        link_tag = card.find('a', href=True)

        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        company = company_tag.get_text(strip=True) if company_tag else "N/A"
        location = location_tag.get_text(strip=True) if location_tag else "N/A"
        url = link_tag['href'] if link_tag else None

        # Sometimes the job URL might be relative, make absolute:
        if url and url.startswith('/'):
            url = "https://www.brightermonday.co.ke" + url

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'url': url,
        })

    return jobs
