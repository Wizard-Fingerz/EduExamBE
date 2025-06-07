from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import CourseProgress, LessonProgress, ExamProgress
from .serializers import (
    CourseProgressSerializer, LessonProgressSerializer,
    ExamProgressSerializer, CourseProgressOverviewSerializer
)
from django.db import models
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Avg, Max
from datetime import timedelta

# Create your views here.

class CourseProgressView(generics.RetrieveUpdateAPIView):
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        course_id = self.kwargs['course_id']
        progress, created = CourseProgress.objects.get_or_create(
            student=self.request.user,
            course_id=course_id
        )
        return progress

class LessonProgressView(generics.RetrieveUpdateAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        lesson_id = self.kwargs['lesson_id']
        progress, created = LessonProgress.objects.get_or_create(
            student=self.request.user,
            lesson_id=lesson_id
        )
        return progress
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Update course progress
        course_progress = CourseProgress.objects.get(
            student=self.request.user,
            course=instance.lesson.module.course
        )
        total_lessons = instance.lesson.module.course.modules.aggregate(
            total_lessons=models.Count('lessons')
        )['total_lessons']
        completed_lessons = course_progress.completed_lessons.count()
        course_progress.progress_percentage = (completed_lessons / total_lessons) * 100
        course_progress.save()
        
        return Response(serializer.data)

class LessonCompletionView(generics.UpdateAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        lesson_id = self.kwargs['lesson_id']
        progress, created = LessonProgress.objects.get_or_create(
            student=self.request.user,
            lesson_id=lesson_id
        )
        return progress
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_completed = True
        instance.completed_at = timezone.now()
        instance.save()
        
        # Update course progress
        course_progress = CourseProgress.objects.get(
            student=self.request.user,
            course=instance.lesson.module.course
        )
        course_progress.completed_lessons.add(instance.lesson)
        
        # Calculate progress percentage
        total_lessons = instance.lesson.module.course.modules.aggregate(
            total_lessons=models.Count('lessons')
        )['total_lessons']
        completed_lessons = course_progress.completed_lessons.count()
        course_progress.progress_percentage = (completed_lessons / total_lessons) * 100
        
        # Check if course is completed
        if completed_lessons == total_lessons:
            course_progress.is_completed = True
            course_progress.completed_at = timezone.now()
        
        course_progress.save()
        
        return Response(self.get_serializer(instance).data)

class ExamProgressView(generics.RetrieveAPIView):
    serializer_class = ExamProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        exam_id = self.kwargs['exam_id']
        progress, created = ExamProgress.objects.get_or_create(
            student=self.request.user,
            exam_id=exam_id
        )
        return progress

class CourseProgressOverviewView(generics.RetrieveAPIView):
    serializer_class = CourseProgressOverviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        course_id = self.kwargs['course_id']
        progress, created = CourseProgress.objects.get_or_create(
            student=self.request.user,
            course_id=course_id
        )
        return progress

class CourseProgressListView(generics.ListAPIView):
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CourseProgress.objects.none()
        return CourseProgress.objects.filter(student=self.request.user)

class CourseProgressDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CourseProgress.objects.none()
        return CourseProgress.objects.filter(student=self.request.user)

class LessonProgressListView(generics.ListAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LessonProgress.objects.none()
        return LessonProgress.objects.filter(student=self.request.user)

class LessonProgressDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LessonProgress.objects.none()
        return LessonProgress.objects.filter(student=self.request.user)

class ExamProgressListView(generics.ListAPIView):
    serializer_class = ExamProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ExamProgress.objects.none()
        return ExamProgress.objects.filter(student=self.request.user)

class ExamProgressDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ExamProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ExamProgress.objects.none()
        return ExamProgress.objects.filter(student=self.request.user)

class LearningJourneyStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get overall statistics
        total_courses = CourseProgress.objects.filter(student=user).count()
        completed_courses = CourseProgress.objects.filter(student=user, is_completed=True).count()
        total_lessons = LessonProgress.objects.filter(student=user).count()
        completed_lessons = LessonProgress.objects.filter(student=user, is_completed=True).count()
        total_exams = ExamProgress.objects.filter(student=user).count()
        
        # Calculate average scores
        avg_exam_score = ExamProgress.objects.filter(
            student=user,
            best_score__isnull=False
        ).aggregate(avg_score=Avg('best_score'))['avg_score'] or 0
        
        # Get time spent learning
        total_time_spent = LessonProgress.objects.filter(
            student=user
        ).aggregate(total_time=models.Sum('time_spent'))['total_time'] or timedelta()
        
        # Get recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_lessons = LessonProgress.objects.filter(
            student=user,
            updated_at__gte=seven_days_ago
        ).count()
        
        return Response({
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'total_exams': total_exams,
            'average_exam_score': round(avg_exam_score, 2),
            'total_time_spent': str(total_time_spent),
            'recent_activity': {
                'lessons_completed': recent_lessons,
                'days_active': 7
            }
        })

class RecentActivityView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        recent_activities = []
        
        # Get recent lesson completions
        recent_lessons = LessonProgress.objects.filter(
            student=user,
            is_completed=True
        ).order_by('-completed_at')[:5]
        
        for lesson in recent_lessons:
            recent_activities.append({
                'type': 'lesson',
                'title': lesson.lesson.title,
                'timestamp': lesson.completed_at,
                'course': lesson.lesson.module.course.title
            })
        
        # Get recent exam attempts
        recent_exams = ExamProgress.objects.filter(
            student=user,
            last_attempt__isnull=False
        ).order_by('-last_attempt')[:5]
        
        for exam in recent_exams:
            recent_activities.append({
                'type': 'exam',
                'title': exam.exam.title,
                'timestamp': exam.last_attempt,
                'score': exam.best_score
            })
        
        # Sort by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response(recent_activities[:10])  # Return top 10 most recent activities

class LearningPathView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id, *args, **kwargs):
        user = request.user
        
        try:
            course_progress = CourseProgress.objects.get(
                student=user,
                course_id=course_id
            )
        except CourseProgress.DoesNotExist:
            return Response(
                {'error': 'Course progress not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all lessons in the course
        lessons = course_progress.course.modules.prefetch_related('lessons').all()
        
        learning_path = []
        for module in lessons:
            module_path = {
                'module': module.title,
                'lessons': []
            }
            
            for lesson in module.lessons.all():
                try:
                    lesson_progress = LessonProgress.objects.get(
                        student=user,
                        lesson=lesson
                    )
                    lesson_status = {
                        'id': lesson.id,
                        'title': lesson.title,
                        'is_completed': lesson_progress.is_completed,
                        'time_spent': str(lesson_progress.time_spent),
                        'last_position': lesson_progress.last_position
                    }
                except LessonProgress.DoesNotExist:
                    lesson_status = {
                        'id': lesson.id,
                        'title': lesson.title,
                        'is_completed': False,
                        'time_spent': '0:00:00',
                        'last_position': 0
                    }
                
                module_path['lessons'].append(lesson_status)
            
            learning_path.append(module_path)
        
        return Response({
            'course': course_progress.course.title,
            'progress_percentage': course_progress.progress_percentage,
            'learning_path': learning_path
        })
