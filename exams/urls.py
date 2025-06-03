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
] 