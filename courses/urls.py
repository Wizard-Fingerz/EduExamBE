from django.urls import path
from . import views
from .subjects.views import SubjectViewSet

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subjects')


urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('create/', views.CourseCreateView.as_view(), name='course-create'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course-update'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('<int:pk>/enroll/', views.CourseEnrollView.as_view(), name='course-enroll'),
    path('<int:pk>/unenroll/', views.CourseUnenrollView.as_view(), name='course-unenroll'),
    path('<int:pk>/students/', views.CourseStudentsView.as_view(), name='course-students'),
    path('<int:pk>/analytics/', views.CourseAnalyticsView.as_view(), name='course-analytics'),
    
    # Staff-specific endpoints
    path('staff/', views.StaffCourseListView.as_view(), name='staff-course-list'),
    path('subjects/', views.StaffSubjectViewSet.as_view(), name='staff-subject-list'),
    path('staff/<int:pk>/', views.StaffCourseDetailView.as_view(), name='staff-course-detail'),
    path('staff/create/', views.StaffCourseCreateView.as_view(), name='staff-course-create'),
    path('staff/<int:pk>/update/', views.StaffCourseUpdateView.as_view(), name='staff-course-update'),
    path('staff/<int:pk>/delete/', views.StaffCourseDeleteView.as_view(), name='staff-course-delete'),
    path('staff/<int:pk>/students/', views.StaffCourseStudentsView.as_view(), name='staff-course-students'),
    path('staff/<int:pk>/analytics/', views.StaffCourseAnalyticsView.as_view(), name='staff-course-analytics'),
    path('<int:pk>/modules/', views.ModuleListView.as_view(), name='module-list'),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<int:pk>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    
    # Assignment endpoints
    path('assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/create/', views.AssignmentCreateView.as_view(), name='assignment-create'),
    path('assignments/<int:pk>/update/', views.AssignmentUpdateView.as_view(), name='assignment-update'),
    path('assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('assignments/<int:pk>/questions/', views.AssignmentQuestionListView.as_view(), name='assignment-question-list'),
    path('assignment-questions/<int:pk>/', views.AssignmentQuestionDetailView.as_view(), name='assignment-question-detail'),
    
    # Staff-specific assignment endpoints
    path('staff/assignments/', views.StaffAssignmentListView.as_view(), name='staff-assignment-list'),
    path('staff/assignments/<int:pk>/', views.StaffAssignmentDetailView.as_view(), name='staff-assignment-detail'),
    path('staff/courses/<int:course_id>/assignments/create/', views.StaffAssignmentCreateView.as_view(), name='staff-assignment-create'),
    path('staff/assignments/<int:pk>/update/', views.StaffAssignmentUpdateView.as_view(), name='staff-assignment-update'),
    path('staff/assignments/<int:pk>/delete/', views.StaffAssignmentDeleteView.as_view(), name='staff-assignment-delete'),
    path('staff/assignments/<int:pk>/analytics/', views.StaffAssignmentAnalyticsView.as_view(), name='staff-assignment-analytics'),
    path('staff/assignments/<int:pk>/questions/', views.AssignmentQuestionListView.as_view(), name='staff-assignment-question-list'),
    path('staff/assignment-questions/<int:pk>/', views.AssignmentQuestionDetailView.as_view(), name='staff-assignment-question-detail'),
] 