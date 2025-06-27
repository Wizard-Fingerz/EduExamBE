from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # Staff-specific endpoints
    path('staff/profile/', views.StaffProfileView.as_view(), name='staff-profile'),
    path('staff/profile/update/', views.StaffProfileUpdateView.as_view(), name='staff-profile-update'),
    path('staff/dashboard/stats/', views.StaffDashboardStatsView.as_view(), name='staff-dashboard-stats'),
    path('students/', views.StaffStudentsView.as_view(), name='staff-students'),
    path('examination-types/', views.ExaminationTypeListView.as_view(), name='examination-type-list'),
] 