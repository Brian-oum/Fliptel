from django.core.management.base import BaseCommand
from Jobs.models import Job
from Jobs.scraper.youngkenyans import scrape_youngkenyans
from Jobs.scraper.brightermonday import scrape_brightermonday
from Jobs.scraper.myjobmag import scrape_myjobmag


class Command(BaseCommand):
    help = 'Scrape jobs from multiple sites'

    def handle(self, *args, **options):
        scrapers = [
            scrape_youngkenyans,
            scrape_brightermonday,
            scrape_myjobmag,
        ]
        for scraper_func in scrapers:
            try:
                jobs_data = scraper_func()
                for job_data in jobs_data:
                    Job.objects.get_or_create(link=job_data['link'], defaults=job_data)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in {scraper_func.__name__}: {e}"))
        self.stdout.write(self.style.SUCCESS('Scraping complete!'))