import requests
from datetime import datetime
from dateutil import parser  # install python-dateutil
from .models import Job

def fetch_jobs_from_api():
    APP_ID = '3de36405'
    APP_KEY = '4a676fc603c8218bb5ec3aaad5363092'
    API_URL = f'https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={APP_ID}&app_key={APP_KEY}'


    saved_count = 0
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        jobs_data = response.json()

        for item in jobs_data.get('results', []):
            title = item.get('title')
            company = item.get('company', {}).get('display_name')
            location = item.get('location', {}).get('display_name')
            description = item.get('description')
            url = item.get('redirect_url')
            posted_str = item.get('created')

            posted_date = None
            if posted_str:
                try:
                    posted_date = parser.isoparse(posted_str)
                except Exception:
                    posted_date = None

            if url and not Job.objects.filter(url=url).exists():
                Job.objects.create(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=url,
                    posted_date=posted_date
                )
                saved_count += 1
    except requests.RequestException as e:
        print(f"Error fetching jobs from API: {e}")

    return saved_count
