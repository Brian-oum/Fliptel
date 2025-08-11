from django.db import models
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    posted_date = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title
