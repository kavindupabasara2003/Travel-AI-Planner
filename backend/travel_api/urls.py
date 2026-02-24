from django.urls import path
from .views import ItineraryAgentView, TripAssistantView

urlpatterns = [
    path('plan/', ItineraryAgentView.as_view(), name='plan_itinerary'),
    path('chat/', TripAssistantView.as_view(), name='trip_chat'),
]
