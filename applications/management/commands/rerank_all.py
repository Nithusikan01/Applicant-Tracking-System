from django.core.management.base import BaseCommand
from django.db import transaction
from jobs.models import Job
from applications.services import rerank_applications


class Command(BaseCommand):
    help = 'Rerank all applications for all jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job-id',
            type=int,
            help='Rerank only applications for specific job ID',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        job_id = options.get('job_id')
        
        if job_id:
            try:
                job = Job.objects.get(pk=job_id)
                self.stdout.write(f'Reranking applications for job: {job.title}')
                rerank_applications(job)
                self.stdout.write(self.style.SUCCESS(f'Successfully reranked job {job_id}'))
            except Job.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Job {job_id} not found'))
        else:
            jobs = Job.objects.all()
            total = jobs.count()
            self.stdout.write(f'Reranking applications for {total} jobs...')
            
            for idx, job in enumerate(jobs, 1):
                self.stdout.write(f'Processing job {idx}/{total}: {job.title}')
                rerank_applications(job)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully reranked all {total} jobs'))