from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(max_length=200, blank=True)
    institution_name = models.CharField(max_length=255, blank=True)
    examination_type = models.ForeignKey('ExaminationType', null=True, blank=True, on_delete=models.SET_NULL)
    grade = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class ExaminationType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
