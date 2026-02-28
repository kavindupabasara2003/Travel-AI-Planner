from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ItineraryAgentView, TripAssistantView, RegisterView, SavedTripView
from .serializers import CustomTokenObtainPairView
from .admin_views import (
    AdminStatsView, AdminUserListView, AdminUserDetailView,
    AdminTripListView, AdminTripDetailView, AdminCacheListView, AdminCacheDetailView
)

urlpatterns = [
    path('plan/', ItineraryAgentView.as_view(), name='plan_itinerary'),
    path('chat/', TripAssistantView.as_view(), name='trip_chat'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('trips/', SavedTripView.as_view(), name='saved_trips'),
    path('trips/<int:pk>/', SavedTripView.as_view(), name='saved_trip_detail'),
    
    # Admin API Routes
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/trips/', AdminTripListView.as_view(), name='admin_trips'),
    path('admin/trips/<int:pk>/', AdminTripDetailView.as_view(), name='admin_trip_detail'),
    path('admin/cache/', AdminCacheListView.as_view(), name='admin_cache'),
    path('admin/cache/<int:pk>/', AdminCacheDetailView.as_view(), name='admin_cache_detail'),
]
