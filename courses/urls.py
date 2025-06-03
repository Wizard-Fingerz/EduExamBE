from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('create/', views.CourseCreateView.as_view(), name='course-create'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course-update'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('<int:pk>/enroll/', views.CourseEnrollView.as_view(), name='course-enroll'),
    path('<int:pk>/modules/', views.ModuleListView.as_view(), name='module-list'),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<int:pk>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
] 