from django.db import models
from django.conf import settings
from courses.models import Course, Lesson
from exams.models import Exam, ExamAttempt

class CourseProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    completed_lessons = models.ManyToManyField(Lesson, blank=True, related_name='completed_by')
    last_accessed_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_accessed_by')
    progress_percentage = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class LessonProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(default=0)
    last_position = models.PositiveIntegerField(default=0)  # For video progress
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'lesson')
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"

class ExamProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_progress')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_progress')
    attempts = models.ManyToManyField(ExamAttempt, related_name='progress')
    best_score = models.PositiveIntegerField(null=True, blank=True)
    last_attempt = models.ForeignKey(ExamAttempt, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_attempt_for')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'exam')
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"
