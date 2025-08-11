from django.shortcuts import render, get_object_or_404
from .models import Job
from .utils import fetch_jobs_from_api

def job_list(request):
    # Optionally call fetch_jobs_from_api here or via scheduled task/cron
    fetch_jobs_from_api()

    jobs = Job.objects.all().order_by('-posted_date')
    return render(request, 'Jobs/job_list.html', {'jobs': jobs})

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'Jobs/job_detail.html', {'job': job})
