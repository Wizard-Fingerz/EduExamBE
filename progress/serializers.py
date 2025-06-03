from rest_framework import serializers
from .models import CourseProgress, LessonProgress, ExamProgress
from courses.serializers import CourseSerializer, LessonSerializer
from exams.serializers import ExamSerializer
from django.db import models

class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = ('id', 'lesson', 'is_completed', 'completed_at', 'time_spent', 'last_position')
        read_only_fields = ('id', 'lesson')

class CourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    completed_lessons = LessonSerializer(many=True, read_only=True)
    last_accessed_lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = ('id', 'course', 'completed_lessons', 'last_accessed_lesson',
                 'progress_percentage', 'is_completed', 'completed_at')
        read_only_fields = ('id', 'course', 'progress_percentage', 'is_completed')

class ExamProgressSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    
    class Meta:
        model = ExamProgress
        fields = ('id', 'exam', 'best_score', 'last_attempt')
        read_only_fields = ('id', 'exam', 'best_score')

class CourseProgressOverviewSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons_count = serializers.SerializerMethodField()
    upcoming_exams = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseProgress
        fields = ('id', 'course', 'progress_percentage', 'total_lessons',
                 'completed_lessons_count', 'upcoming_exams')
    
    def get_total_lessons(self, obj):
        return obj.course.modules.aggregate(
            total_lessons=models.Count('lessons')
        )['total_lessons']
    
    def get_completed_lessons_count(self, obj):
        return obj.completed_lessons.count()
    
    def get_upcoming_exams(self, obj):
        from django.utils import timezone
        upcoming_exams = obj.course.exams.filter(
            start_time__gt=timezone.now(),
            is_published=True
        ).order_by('start_time')[:5]
        return ExamSerializer(upcoming_exams, many=True).data 