from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True, null=True, blank=True)  # From previous fix
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank= True)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Allow null temporarily

    def __str__(self):
        return self.title