from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam-list'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam-detail'),
    path('create/', views.ExamCreateView.as_view(), name='exam-create'),
    path('<int:pk>/update/', views.ExamUpdateView.as_view(), name='exam-update'),
    path('<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam-delete'),
    path('<int:pk>/questions/', views.QuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('<int:pk>/attempt/', views.ExamAttemptView.as_view(), name='exam-attempt'),
    path('attempts/<int:pk>/', views.ExamAttemptDetailView.as_view(), name='attempt-detail'),
    path('attempts/<int:pk>/submit/', views.ExamSubmissionView.as_view(), name='exam-submit'),
    
    # Staff-specific endpoints
    path('staff/', views.StaffExamListView.as_view(), name='staff-exam-list'),
    path('staff/<int:pk>/', views.StaffExamDetailView.as_view(), name='staff-exam-detail'),
    path('staff/courses/<int:course_id>/exams/create/', views.StaffExamCreateView.as_view(), name='staff-exam-create'),
    path('staff/<int:pk>/update/', views.StaffExamUpdateView.as_view(), name='staff-exam-update'),
    path('staff/<int:pk>/delete/', views.StaffExamDeleteView.as_view(), name='staff-exam-delete'),
    path('staff/<int:pk>/analytics/', views.StaffExamAnalyticsView.as_view(), name='staff-exam-analytics'),
] 