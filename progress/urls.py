from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('course/<int:course_id>/', views.CourseProgressView.as_view(), name='course-progress'),
    path('lesson/<int:lesson_id>/', views.LessonProgressView.as_view(), name='lesson-progress'),
    path('exam/<int:exam_id>/', views.ExamProgressView.as_view(), name='exam-progress'),
    path('lesson/<int:lesson_id>/complete/', views.LessonCompletionView.as_view(), name='lesson-complete'),
    path('course/<int:course_id>/overview/', views.CourseProgressOverviewView.as_view(), name='course-progress-overview'),
    
    path('learning-journey/stats/', views.LearningJourneyStatsView.as_view(), name='learning-journey-stats'),
    path('learning-journey/recent-activity/', views.RecentActivityView.as_view(), name='recent-activity'),
    path('learning-journey/path/<int:course_id>/', views.LearningPathView.as_view(), name='learning-path'),
    
    path('courses/', views.CourseProgressListView.as_view(), name='course-progress-list'),
    path('lessons/', views.LessonProgressListView.as_view(), name='lesson-progress-list'),
    path('exams/', views.ExamProgressListView.as_view(), name='exam-progress-list'),
] 