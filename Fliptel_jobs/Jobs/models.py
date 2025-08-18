# jobs/models.py
from django.db import models
from django.utils import timezone

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('CT', 'Contract'),
        ('IN', 'Internship'),
    ]

    FACULTY_CHOICES = [
        ('IT', 'Information Technology'),
        ('BUS', 'Business & Finance'),
        ('ENG', 'Engineering'),
        ('MED', 'Medicine & Health'),
        ('EDU', 'Education'),
        ('ART', 'Arts & Design'),
        ('SCI', 'Science & Research'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES)
    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, default='IT')
    description = models.TextField()
    url = models.URLField(blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)

