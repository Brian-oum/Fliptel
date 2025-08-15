from django.shortcuts import render
from .models import Job

def job_list(request):
    jobs = Job.objects.all().order_by('-pub_date')
    return render(request, 'Jobs/job_list.html', {'jobs': jobs})
