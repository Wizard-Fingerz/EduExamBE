from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone

from courses.subjects.models import Subject
from .models import Exam, Question, ExamAttempt, Answer
from .serializers import (
    ExamSerializer, ExamCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    ExamAttemptSerializer, ExamSubmissionSerializer,
    StaffExamCreateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from courses.models import Course
from django.db.models import Avg, Count

# Create your views here.

class ExamListView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Exam.objects.none()
        
        user = self.request.user
        if not user.is_authenticated:
            return Exam.objects.none()
        if hasattr(user, 'user_type'):
            if user.user_type == 'teacher':
                return Exam.objects.all().order_by('-year')  # Order by year descending
            elif user.user_type == 'student':
                # Only exams for courses the student is enrolled in
                return Exam.objects.filter(examination_type=user.examination_type).order_by('-year')
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
            return Exam.objects.all().order_by('-year')
        elif user.user_type == 'student':
            return Exam.objects.filter(examination_type=user.examination_type).order_by('-year')
        return Exam.objects.none()

class ExamCreateView(generics.CreateAPIView):
    serializer_class = ExamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'teacher':
            raise PermissionDenied("Only teachers can create exams.")
        subject_id = self.request.data.get('subject')
        if not subject_id:
            raise PermissionDenied("Subject ID is required.")
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            raise PermissionDenied("Subject not found.")
        serializer.save(subject=subject)

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
        # Handle both 'pk' and 'exam_id' URL parameters
        exam_id = self.kwargs.get('pk') or self.kwargs.get('exam_id')
        return Question.objects.filter(exam_id=exam_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionSerializer
    
    def perform_create(self, serializer):
        # Handle both 'pk' and 'exam_id' URL parameters
        exam_id = self.kwargs.get('pk') or self.kwargs.get('exam_id')
        exam = Exam.objects.get(id=exam_id)
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
        serializer.save(student=self.request.user, exam=exam)  # Pass exam here

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

class StaffExamListView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Exam.objects.all().order_by('-year')

class StaffExamDetailView(generics.RetrieveAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return exam

class StaffExamCreateView(generics.CreateAPIView):
    serializer_class = StaffExamCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'teacher':
            raise PermissionDenied("Only teachers can create exams.")
        
        subject_id = self.request.data.get('subject')
        if not subject_id:
            raise PermissionDenied("Course ID is required.")
        
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            raise PermissionDenied("Course not found.")
        
        
        # Save the exam with the course
        serializer.save(subject=subject)

class StaffExamUpdateView(generics.UpdateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher' or exam.course.instructor != self.request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return exam

class StaffExamDeleteView(generics.DestroyAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher' or exam.course.instructor != self.request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return exam

class StaffExamAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        if request.user.user_type != 'teacher' or exam.course.instructor != request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        attempts = ExamAttempt.objects.filter(exam=exam)
        total_attempts = attempts.count()
        completed_attempts = attempts.filter(submitted_at__isnull=False).count()
        average_score = attempts.filter(submitted_at__isnull=False).aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0

        return Response({
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'average_score': average_score,
            'passing_rate': (attempts.filter(score__gte=exam.passing_marks).count() / completed_attempts * 100) if completed_attempts > 0 else 0
        })
