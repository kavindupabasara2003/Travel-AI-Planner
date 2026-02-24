from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ItineraryAgentView, TripAssistantView, RegisterView, SavedTripView

urlpatterns = [
    path('plan/', ItineraryAgentView.as_view(), name='plan_itinerary'),
    path('chat/', TripAssistantView.as_view(), name='trip_chat'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('trips/', SavedTripView.as_view(), name='saved_trips'),
    path('trips/<int:pk>/', SavedTripView.as_view(), name='saved_trip_detail'),
]
