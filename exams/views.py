from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Exam, Question, ExamAttempt, Answer
from .serializers import (
    ExamSerializer, ExamCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    ExamAttemptSerializer, ExamSubmissionSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class ExamListView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
            
        user = self.request.user
        if user.user_type == 'teacher':
            return Exam.objects.filter(course__instructor=user)
        elif user.user_type == 'student':
            return Exam.objects.filter(course__students=user)
        return Exam.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamCreateSerializer
        return ExamSerializer
    
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.instructor != self.request.user:
            raise permissions.PermissionDenied("Only the course instructor can create exams.")
        serializer.save()

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExamCreateSerializer
        return ExamSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
            
        user = self.request.user
        if user.user_type == 'teacher':
            return Exam.objects.filter(course__instructor=user)
        elif user.user_type == 'student':
            return Exam.objects.filter(course__students=user)
        return Exam.objects.none()

class ExamCreateView(generics.CreateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'teacher':
            raise PermissionDenied("Only teachers can create exams.")
        serializer.save(course_id=self.kwargs['course_id'])

class ExamUpdateView(generics.UpdateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Exam.objects.filter(course__instructor=self.request.user)

class ExamDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Exam.objects.filter(course__instructor=self.request.user)

class QuestionListView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Question.objects.none()
        return Question.objects.filter(exam_id=self.kwargs['pk'])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionSerializer
    
    def perform_create(self, serializer):
        exam = Exam.objects.get(id=self.kwargs['pk'])
        if exam.course.instructor != self.request.user:
            raise permissions.PermissionDenied("Only the course instructor can add questions.")
        serializer.save(exam=exam)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuestionCreateSerializer
        return QuestionSerializer

class ExamAttemptView(generics.CreateAPIView):
    serializer_class = ExamAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        exam = Exam.objects.get(id=self.kwargs['pk'])
        if exam.course.students.filter(id=self.request.user.id).exists():
            serializer.save(student=self.request.user, exam=exam)
        else:
            raise permissions.PermissionDenied("You are not enrolled in this course.")

class ExamAttemptDetailView(generics.RetrieveAPIView):
    serializer_class = ExamAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExamAttempt.objects.filter(student=self.request.user)

class ExamSubmissionView(generics.CreateAPIView):
    serializer_class = ExamSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        attempt = ExamAttempt.objects.get(id=self.kwargs['pk'])
        if attempt.student != self.request.user:
            raise permissions.PermissionDenied("You can only submit your own exam attempts.")
        if attempt.is_completed:
            raise permissions.PermissionDenied("This exam attempt has already been completed.")
        serializer.save(attempt=attempt)
