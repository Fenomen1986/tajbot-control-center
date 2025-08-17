#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controlcenter.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # --- НАША НОВАЯ ЛОГИКА АВТО-СОЗДАНИЯ АДМИНА ---
    try:
        # Проверяем, запущена ли команда создания таблиц, чтобы создать админа ПОСЛЕ нее
        if 'migrate' in sys.argv and len(sys.argv) > 1:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            ADMIN_USERNAME = os.environ.get('ADMIN_USER')
            ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
            ADMIN_PASSWORD = os.environ.get('ADMIN_PASS')

            if ADMIN_USERNAME and ADMIN_EMAIL and ADMIN_PASSWORD:
                if not User.objects.filter(username=ADMIN_USERNAME).exists():
                    print("Creating admin account...")
                    User.objects.create_superuser(
                        username=ADMIN_USERNAME,
                        email=ADMIN_EMAIL,
                        password=ADMIN_PASSWORD
                    )
                    print("Admin account created successfully.")
                else:
                    print("Admin account already exists.")
            else:
                print("Admin credentials not found in environment variables. Skipping creation.")

    except Exception as e:
        print(f"An error occurred during admin creation: {e}")
    # --- КОНЕЦ НАШЕЙ ЛОГИКИ ---

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()