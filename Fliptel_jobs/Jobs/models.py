from django.db import models

# Create your models here.
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    date_posted = models.DateField()
    source = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def get_signed_id(self):
        from django.core.signing import TimestampSigner
        return TimestampSigner().sign(self.id)
