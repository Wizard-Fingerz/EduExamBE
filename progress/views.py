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
