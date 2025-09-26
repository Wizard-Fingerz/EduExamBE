import datetime
import csv
import requests
from users.models import ExaminationType
from exams.models import Exam, Question, Choice
import os
from bs4 import BeautifulSoup
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, pagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from courses.subjects.models import Subject
from .models import Exam, Question, ExamAttempt, Answer
from .serializers import (
    ExamSerializer, ExamCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    ExamAttemptSerializer, ExamSubmissionSerializer, ScrapeQuestionsSerializer,
    StaffExamCreateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from courses.models import Course
from django.db.models import Avg, Count

# Create your views here.


class CustomPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 12

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'num_pages': self.page.paginator.num_pages,
            'page_size': self.page_size,
            'current_page': self.page.number,
            'results': data
        })


class ExamListView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination  # <-- Add this line

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
            raise permissions.PermissionDenied(
                "Only the course instructor can create exams.")
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
    pagination_class = CustomPagination  # <-- Add this line

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
            raise permissions.PermissionDenied(
                "You can only submit your own exam attempts.")
        if attempt.is_completed:
            raise permissions.PermissionDenied(
                "This exam attempt has already been completed.")
        serializer.save(attempt=attempt)


class StaffExamListView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination  # <-- Add this line

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
        completed_attempts = attempts.filter(
            submitted_at__isnull=False).count()
        average_score = attempts.filter(submitted_at__isnull=False).aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0

        return Response({
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'average_score': average_score,
            'passing_rate': (attempts.filter(score__gte=exam.passing_marks).count() / completed_attempts * 100) if completed_attempts > 0 else 0
        })


class ScrapeQuestionsAPIView(APIView):

    authentication_classes = []  # ⛔ No auth
    permission_classes = [AllowAny]  # ✅ Open to all


    @swagger_auto_schema(request_body=ScrapeQuestionsSerializer)

    def post(self, request):
        serializer = ScrapeQuestionsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated fields
        subject_name = serializer.validated_data['subject']
        year = serializer.validated_data['year']
        max_pages = serializer.validated_data['pages']
        slug = serializer.validated_data['slug']

        if not all([subject_name, year, slug]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        BASE_URL = 'https://nigerianscholars.com'
        BASE_PATH = f'/past-questions/{slug}/jamb/year/{year}/'
        HEADERS = {
            "User-Agent": "Mozilla/5.0"
        }

        questions = []

        for page in range(1, max_pages + 1):
            if page == 1:
                url = BASE_URL + BASE_PATH
            else:
                url = f"{BASE_URL}{BASE_PATH}page/{page}/"

            print(f"Scraping: {url}")
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')

            page_questions = []
            for q_div in soup.select('.question_block'):
                question_el = q_div.select_one('.question_text')
                question_text = question_el.get_text(
                    strip=True) if question_el else None

                options = [opt.get_text(strip=True)
                           for opt in q_div.select('.q_option')]

                answer_el = q_div.select_one('.ans_label')
                answer = answer_el.get_text(strip=True) if answer_el else None

                page_questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': answer
                })

            if not page_questions:
                break
            questions.extend(page_questions)

        # Save to DB
        subject, _ = Subject.objects.get_or_create(name=subject_name)
        exam, _ = Exam.objects.get_or_create(
            subject=subject,
            title=f"JAMB {year} {subject_name}",
            examination_type=ExaminationType.objects.get(name='JAMB'),
            defaults={
                "description": f"JAMB {year} {subject_name} Questions",
                "duration": timezone.timedelta(seconds=3600),
                "total_marks": 100,
                "year": year,
                "passing_marks": 40,
                "start_time": timezone.now(),
                "end_time": timezone.now() + timezone.timedelta(hours=1),
                "is_published": True,
            }
        )

        for idx, q in enumerate(questions, start=1):
            question_obj = Question.objects.create(
                exam=exam,
                question_text=q['question'],
                question_type='multiple_choice',
                marks=1,
                order=idx
            )
            for opt in q['options']:
                is_correct = (opt == q['answer'])
                Choice.objects.create(
                    question=question_obj,
                    choice_text=opt,
                    is_correct=is_correct
                )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f'scraped_questions_{timestamp}.csv'
        csv_path = os.path.join("media", csv_filename)

        os.makedirs("media", exist_ok=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['question_text', 'option_1', 'option_2',
                            'option_3', 'option_4', 'correct_option'])
            for q in questions:
                row = [
                    q['question'],
                    q['options'][0] if len(q['options']) > 0 else '',
                    q['options'][1] if len(q['options']) > 1 else '',
                    q['options'][2] if len(q['options']) > 2 else '',
                    q['options'][3] if len(q['options']) > 3 else '',
                    q['answer'] or ''
                ]
                writer.writerow(row)

        return Response({
            "message": "Scraping complete",
            "questions_scraped": len(questions),
            "csv_file": csv_filename
        }, status=200)
