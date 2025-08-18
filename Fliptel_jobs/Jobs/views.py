from django.shortcuts import render
from django.db.models import Q
from .models import Job

def job_list(request):
    jobs = Job.objects.all()

    # Filters
    query = request.GET.get('q')
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')
    faculty = request.GET.get('faculty')

    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if faculty:
        jobs = jobs.filter(faculty=faculty)

    # Distinct options for filters
    locations = Job.objects.values_list('location', flat=True).distinct()
    job_types = Job.JOB_TYPE_CHOICES
    faculties = Job.FACULTY_CHOICES

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'locations': locations,
        'job_types': job_types,
        'faculties': faculties,
    })
