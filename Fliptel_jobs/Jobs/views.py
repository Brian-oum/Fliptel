from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Job

def job_list(request):
    jobs = Job.objects.all().order_by('-posted_date')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

def view_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})
