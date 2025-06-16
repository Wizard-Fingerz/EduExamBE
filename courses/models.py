from django.db import models
from django.conf import settings
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_teaching')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_enrolled', through='CourseEnrollment')
    price = models.DecimalField(max_digits=10, decimal_places=2, null= True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100,  null = True, blank = True)
    level = models.CharField(max_length=50, null = True, blank = True)
    duration = models.IntegerField(default=2)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    ratings = models.ManyToManyField(settings.AUTH_USER_MODEL, through='CourseRating', related_name='rated_courses')

    def __str__(self):
        return self.title

class CourseEnrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    completion_status = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage of completion

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class CourseRating(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.rating}"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    duration = models.IntegerField(default=120)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"
