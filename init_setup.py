import os
import django
from django.core.management import call_command
from django.contrib.auth import get_user_model

def setup_database():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
    django.setup()
    
    # Run migrations
    print("Running migrations...")
    call_command('makemigrations')
    call_command('migrate')
    
    # Create superuser
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='admin'
        )
        print("Superuser created successfully!")
    else:
        print("Superuser already exists.")
    
    print("Database setup completed!")

if __name__ == '__main__':
    setup_database() 