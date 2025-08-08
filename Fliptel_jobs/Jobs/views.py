from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, HttpResponse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from .models import Job

signer = TimestampSigner()

def job_list(request):
    jobs = Job.objects.all().order_by('-date_posted')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

def view_job(request, signed_job_id):
    try:
        job_id = signer.unsign(signed_job_id, max_age=86400)
        job = Job.objects.get(id=job_id)
        return render(request, 'jobs/job_detail.html', {'job': job})
    except SignatureExpired:
        return HttpResponse("This job link has expired.", status=403)
    except BadSignature:
        return HttpResponse("Invalid job link.", status=400)
    except Job.DoesNotExist:
        return HttpResponse("Job not found.", status=404)
