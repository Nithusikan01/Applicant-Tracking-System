from django.core.management.base import BaseCommand
from applications.tasks import health_check


class Command(BaseCommand):
    help = 'Test Celery connection and task execution'

    def handle(self, *args, **options):
        self.stdout.write('Testing Celery...')
        
        try:
            # Send async task
            result = health_check.delay()
            self.stdout.write(f'Task ID: {result.id}')
            
            # Wait for result (timeout 10 seconds)
            output = result.get(timeout=10)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Celery is working! Response: {output}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Celery test failed: {e}'))