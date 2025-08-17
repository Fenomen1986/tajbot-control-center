import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates an admin user non-interactively from environment variables.'

    def handle(self, *args, **options):
        User = get_user_model()
        ADMIN_USERNAME = os.environ.get('ADMIN_USER')
        ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASS')

        if not all([ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD]):
            self.stdout.write(self.style.ERROR('Admin credentials not found in environment variables. Aborting.'))
            return

        if not User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write(self.style.SUCCESS(f'Creating admin account for {ADMIN_USERNAME}'))
            User.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD
            )
            self.stdout.write(self.style.SUCCESS('Admin account created successfully.'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin account for {ADMIN_USERNAME} already exists.'))