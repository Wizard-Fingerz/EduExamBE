from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Course, Module, Lesson
from .serializers import (
    CourseSerializer, CourseCreateSerializer,
    ModuleSerializer, ModuleCreateSerializer,
    LessonSerializer, LessonCreateSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
