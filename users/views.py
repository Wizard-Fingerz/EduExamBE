from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserProfileSerializer, ExaminationTypeSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from courses.models import Course, CourseEnrollment
from exams.models import Exam
from progress.models import CourseProgress
from django.db.models import Avg, Sum
from django.utils import timezone
from .models import ExaminationType

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        print(self.request.data)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class StaffProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        if self.request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return self.request.user

class StaffProfileUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        if self.request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return self.request.user

class StaffStudentsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        if request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        students = User.objects.filter(user_type='student').order_by('first_name', 'last_name')
        
        student_data = []
        for student in students:
            # Get enrollment info using CourseEnrollment model directly
            enrollments = CourseEnrollment.objects.filter(student=student)
            total_courses = enrollments.count()
            
            # Calculate GPA (average of all course progress percentages)
            course_progresses = CourseProgress.objects.filter(student=student)
            if course_progresses.exists():
                avg_progress = course_progresses.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0
                gpa = (avg_progress / 100) * 4.0  # Convert percentage to 4.0 scale
            else:
                gpa = 0.0
            
            # Get enrollment date (earliest enrollment)
            if enrollments.exists():
                enrollment_date = enrollments.earliest('enrollment_date').enrollment_date
            else:
                enrollment_date = student.date_joined
            
            student_data.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email,
                'studentId': student.username,  # Using username as student ID
                'enrollmentDate': enrollment_date.isoformat(),
                'program': 'General Studies',  # Default program
                'status': 'Active' if student.is_active else 'Inactive',
                'gpa': round(gpa, 2),
                'totalCourses': total_courses,
            })
        
        return Response(student_data)

class StaffDashboardStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        if request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get total students
        total_students = User.objects.filter(user_type='student').count()
        
        # Get total courses
        total_courses = Course.objects.filter(instructor=request.user).count()
        
        # Get total exams
        total_exams = Exam.objects.all().count()
        
        # Get active exams
        active_exams = Exam.objects.filter(
            is_published=True
        ).count()
        
        # Get recent enrollments (last 30 days)
        recent_enrollments = Course.objects.filter(
            instructor=request.user,
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Get total revenue
        courses = Course.objects.filter(instructor=request.user)
        total_revenue = courses.aggregate(
            total=Sum('price')
        )['total'] or 0
        
        return Response({
            'total_students': total_students,
            'total_courses': total_courses,
            'total_exams': total_exams,
            'active_exams': active_exams,
            'recent_enrollments': recent_enrollments,
            'total_revenue': total_revenue
        })

class ExaminationTypeListView(generics.ListAPIView):
    queryset = ExaminationType.objects.all()
    serializer_class = ExaminationTypeSerializer
    permission_classes = (permissions.AllowAny,)
