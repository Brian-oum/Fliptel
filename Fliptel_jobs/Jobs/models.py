# jobs/models.py
from django.db import models
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, default='')
    location = models.CharField(max_length=255,default='Kenya')
    description = models.TextField( default='')
    job_type = models.CharField(max_length=100,default='',choices=[
        ('tech', 'Technology'),
        ('business', 'Business'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    ])
    posted_date = models.DateTimeField(default=timezone.now)
    url = models.URLField(blank=True, null=True)  # optional if you want external links

    def __str__(self):
        return self.title
