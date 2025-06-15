from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Course, Module, Lesson, CourseEnrollment
from .serializers import (
    CourseSerializer, CourseCreateSerializer,
    ModuleSerializer, ModuleCreateSerializer,
    LessonSerializer, LessonCreateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

# Create your views here.

class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all courses. For teachers, shows their created courses. For students, shows enrolled courses.",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search courses by title or description",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'category',
                openapi.IN_QUERY,
                description="Filter courses by category",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: CourseSerializer(many=True),
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
            
        user = self.request.user
        queryset = Course.objects.all()

        # Add search functionality
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | \
                      queryset.filter(description__icontains=search_query)

        # Add category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        if user.user_type == 'teacher':
            return queryset.filter(instructor=user)
        elif user.user_type == 'student':
            return queryset
        return queryset.none()

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class CourseUpdateView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        return Course.objects.filter(instructor=self.request.user)

class CourseDeleteView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()
        return Course.objects.filter(instructor=self.request.user)

class CourseEnrollView(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user in course.students.all():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        course.students.add(request.user)
        return Response(self.get_serializer(course).data)

    def delete(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user not in course.students.all():
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        course.students.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CourseUnenrollView(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user not in course.students.all():
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        course.students.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ModuleListView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Module.objects.none()
        return Module.objects.filter(course_id=self.kwargs['pk'])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ModuleCreateSerializer
        return ModuleSerializer
    
    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['pk'])
        if course.instructor != self.request.user:
            raise permissions.PermissionDenied("Only the course instructor can add modules.")
        serializer.save(course=course)

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ModuleCreateSerializer
        return ModuleSerializer

class LessonListView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()
        return Lesson.objects.filter(module_id=self.kwargs['pk'])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonCreateSerializer
        return LessonSerializer
    
    def perform_create(self, serializer):
        module = Module.objects.get(id=self.kwargs['pk'])
        if module.course.instructor != self.request.user:
            raise permissions.PermissionDenied("Only the course instructor can add lessons.")
        serializer.save(module=module)

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LessonCreateSerializer
        return LessonSerializer

class StaffCourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return Course.objects.filter(instructor=self.request.user)

class StaffCourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher' or course.instructor != self.request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return course

class StaffCourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.user_type != 'teacher':
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(instructor=self.request.user)

class StaffCourseUpdateView(generics.UpdateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher' or course.instructor != self.request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return course

class StaffCourseDeleteView(generics.DestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if self.request.user.user_type != 'teacher' or course.instructor != self.request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        return course

class StaffCourseStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if request.user.user_type != 'teacher' or course.instructor != request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        students = course.students.all()
        return Response({
            'total_students': students.count(),
            'students': [
                {
                    'id': student.id,
                    'username': student.username,
                    'email': student.email,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'enrolled_at': student.enrollment_set.get(course=course).enrolled_at
                }
                for student in students
            ]
        })

class StaffCourseAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if request.user.user_type != 'teacher' or course.instructor != request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        total_students = course.students.count()
        total_revenue = course.price * total_students
        average_rating = course.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

        return Response({
            'total_students': total_students,
            'total_revenue': total_revenue,
            'average_rating': average_rating,
            'enrollment_trend': {
                'last_30_days': course.enrollment_set.filter(
                    enrolled_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
            }
        })

class CourseStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
            if request.user.user_type == 'teacher' and course.instructor != request.user:
                return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
            students = course.students.all()
            return Response({
                'course': course.title,
                'students': [
                    {
                        'id': student.id,
                        'username': student.username,
                        'email': student.email,
                        'enrollment_date': CourseEnrollment.objects.get(
                            student=student,
                            course=course
                        ).enrollment_date
                    }
                    for student in students
                ]
            })
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)

class CourseAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
            if request.user.user_type == 'teacher' and course.instructor != request.user:
                return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
            total_students = course.students.count()
            total_revenue = total_students * course.price
            average_rating = course.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
            
            # Get enrollment trends (last 6 months)
            six_months_ago = timezone.now() - timezone.timedelta(days=180)
            enrollments = CourseEnrollment.objects.filter(
                course=course,
                enrollment_date__gte=six_months_ago
            ).values('enrollment_date__month').annotate(
                count=Count('id')
            ).order_by('enrollment_date__month')
            
            return Response({
                'course': course.title,
                'total_students': total_students,
                'total_revenue': total_revenue,
                'average_rating': average_rating,
                'enrollment_trends': [
                    {
                        'month': enrollment['enrollment_date__month'],
                        'count': enrollment['count']
                    }
                    for enrollment in enrollments
                ]
            })
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
