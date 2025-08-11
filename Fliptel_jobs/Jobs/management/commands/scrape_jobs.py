from django.db import models
from django.utils.text import slugify


class JobSource(models.Model):
    """
    Stores info about job source websites (API or scraped).
    """
    name = models.CharField(max_length=255, unique=True)
    base_url = models.URLField()
    source_type = models.CharField(
        max_length=20,
        choices=[
            ('api', 'API'),
            ('scrape', 'Web Scraping')
        ]
    )
    api_endpoint = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class JobCategory(models.Model):
    """
    Categories like IT, Healthcare, Finance, etc.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Main job listing model.
    """
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    posted_date = models.DateTimeField()
    source = models.CharField(max_length=100, null=True, blank=True, default='unknown')


    def __str__(self):
        return f"{self.title} at {self.company}"
