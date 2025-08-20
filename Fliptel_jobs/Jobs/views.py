from django.shortcuts import render
from .models import Job

def job_list(request, faculty=None):
    jobs = Job.objects.all()

    # Faculty filter from URL
    if faculty:
        jobs = jobs.filter(faculty=faculty)

    # Other filters from search
    query = request.GET.get('q')
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')

    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(description__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    locations = Job.objects.values_list('location', flat=True).distinct()
    job_types = Job.JOB_TYPE_CHOICES
    faculties = Job.FACULTY_CHOICES

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'locations': locations,
        'job_types': job_types,
        'faculties': faculties,
        'selected_faculty': faculty,  # for heading + empty state
    })
