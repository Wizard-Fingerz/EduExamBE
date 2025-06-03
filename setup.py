import os
import subprocess
import sys

def run_command(command):
    subprocess.run(command, shell=True, check=True)

def setup_project():
    # Create Django project
    run_command('django-admin startproject elearning .')
    
    # Create apps
    apps = ['users', 'courses', 'exams', 'materials', 'progress']
    for app in apps:
        run_command(f'python manage.py startapp {app}')
    
    print("Project structure created successfully!")

if __name__ == '__main__':
    setup_project() 