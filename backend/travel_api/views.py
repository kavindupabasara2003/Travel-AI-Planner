from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings

from .authentication import MongoAuthentication
from .services.llama_service import LLaMAService

class ItineraryAgentView(APIView):
    """
    POST /api/v1/plan/
    Body: { "preferences": "I want a 7 day honeymoon in the hill country" }
    """
    authentication_classes = [MongoAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = request.data.get("preferences")
        
        if not preferences:
            return Response({"error": "Preferences are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Initialize Service
            # Note: In a real app we might inject this or keep a singleton
            agent = LLaMAService()
            
            # Generate Logic
            itinerary_json = agent.generate_itinerary(preferences)
            
            print("\n--- DEBUG: GENERATED ITINERARY ---")
            print(itinerary_json)
            print("----------------------------------\n")

            if "error" in itinerary_json:
                 return Response(itinerary_json, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(itinerary_json, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .services.trip_assistant import TripAssistantService

class TripAssistantView(APIView):
    """
    POST /api/v1/chat/
    Body: { "location": "Kandy", "query": "Should I go now?", "lat": 7.29, "lon": 80.63 }
    Context-aware Helper (Phase 2)
    """
    authentication_classes = [MongoAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        location = request.data.get("location")
        query = request.data.get("query")
        lat = request.data.get("lat")
        lon = request.data.get("lon")
        activity = request.data.get("activity")
        description = request.data.get("description")
        theme = request.data.get("theme")
        
        if not location or not query:
             return Response({"error": "Location and Query are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assistant = TripAssistantService()
            advice = assistant.get_advice(query, location, lat, lon, activity, description, theme)
            
            return Response({"advice": advice}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
