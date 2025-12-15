from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Create user profiles for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'ADMIN' if user.is_superuser else 'RECRUITER',
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created profile for {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} profiles')
        )