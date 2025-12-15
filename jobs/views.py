from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Job
from .forms import JobForm


def public_job_list(request):
    """Public view of all jobs - no authentication required"""
    jobs = Job.objects.all()
    return render(request, 'jobs/public_job_list.html', {'jobs': jobs})


@login_required
def job_list(request):
    """
    Recruiter view of all jobs
    Optimized with prefetch_related for application counts
    """
    jobs = Job.objects.prefetch_related('application_set').all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@login_required
@transaction.atomic
def job_create(request):
    """Create a new job posting"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Job "{job.title}" created successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Create'})


@login_required
def job_detail(request, pk):
    """
    View job details and applications
    Optimized with select_related for better query performance
    """
    job = get_object_or_404(Job, pk=pk)
    applications = job.application_set.select_related('job').order_by('-match_score', '-created_at')
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'applications': applications
    })


@login_required
@transaction.atomic
def job_edit(request, pk):
    """Edit an existing job"""
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            
            # Rerank applications if job description changed
            if 'description' in form.changed_data:
                from applications.services import rerank_applications
                rerank_applications(job)
                messages.success(
                    request, 
                    f'Job "{job.title}" updated and applications re-ranked!'
                )
            else:
                messages.success(request, f'Job "{job.title}" updated successfully!')
            
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'action': 'Edit',
        'job': job
    })


@login_required
@transaction.atomic
def job_delete(request, pk):
    """Delete a job"""
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect('jobs:job_list')
    
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})