from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Job
from .models import Application
from .forms import ApplicationForm, ApplicationUpdateForm
from .services import extract_resume_text, rerank_applications


def apply(request, job_pk):
    """Public application form for a job"""
    job = get_object_or_404(Job, pk=job_pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            
            # Extract resume text
            resume_text = extract_resume_text(application.resume)
            application.resume_text = resume_text
            application.save(update_fields=['resume_text'])
            
            # Rerank all applications for this job
            rerank_applications(job)
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('applications:apply_success')
    else:
        form = ApplicationForm()
    
    return render(request, 'applications/apply.html', {
        'form': form,
        'job': job
    })


def apply_success(request):
    """Success page after application submission"""
    return render(request, 'applications/apply_success.html')


@login_required
def application_detail(request, pk):
    """View and manage a specific application"""
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('applications:application_detail', pk=application.pk)
    else:
        form = ApplicationUpdateForm(instance=application)
    
    return render(request, 'applications/application_detail.html', {
        'application': application,
        'form': form
    })
