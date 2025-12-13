from django.db import models
from jobs.models import Job


class Application(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('REVIEW', 'Under Review'),
        ('INTERVIEW', 'Interview'),
        ('REJECTED', 'Rejected'),
        ('HIRED', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    resume_text = models.TextField(blank=True)
    match_score = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_score', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.job.title}"