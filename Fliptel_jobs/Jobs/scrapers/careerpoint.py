import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_careerpoint():
    url = "https://www.careerpointkenya.co.ke/category/job-vacancies/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    jobs = []
    posts = soup.select('h2.entry-title a')

    for post in posts:
        title = post.text
        job_url = post['href']
        job_page = requests.get(job_url)
        job_soup = BeautifulSoup(job_page.text, 'lxml')
        description = job_soup.select_one('.entry-content').get_text(strip=True)[:500]

        jobs.append({
            'title': title,
            'company': "CareerPoint Kenya",
            'location': "Kenya",
            'description': description,
            'url': job_url,
            'posted_date': datetime.now().date(),
            'source': "CareerPoint Kenya"
        })

    return jobs
