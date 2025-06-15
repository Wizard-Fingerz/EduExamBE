from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from courses.models import Course
from exams.models import Exam
from progress.models import CourseProgress
from django.db.models import Avg, Sum
from django.utils import timezone

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
        total_exams = Exam.objects.filter(course__instructor=request.user).count()
        
        # Get active exams
        active_exams = Exam.objects.filter(
            course__instructor=request.user,
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
