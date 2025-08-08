from django.core.management.base import BaseCommand
from Jobs.scrapers.careerpoint import scrape_careerpoint
from Jobs.models import Job

class Command(BaseCommand):
    help = "Fetch jobs from CareerPoint Kenya"

    def handle(self, *args, **kwargs):
        jobs = scrape_careerpoint()
        for job in jobs:
            Job.objects.get_or_create(
                title=job['title'],
                company=job['company'],
                url=job['url'],
                defaults={
                    'location': job['location'],
                    'description': job['description'],
                    'date_posted': job['date_posted'],
                    'source': job['source']
                }
            )
        self.stdout.write(self.style.SUCCESS("Jobs fetched and saved."))
