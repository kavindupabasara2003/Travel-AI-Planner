from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services.llama_service import LLaMAService
from .services.trip_assistant import TripAssistantService

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('email') # Use email as username for simplicity
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error': 'Please provide email and password'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()
        return Response({'message': 'User created successfully', 'user_id': user.id}, status=status.HTTP_201_CREATED)

from .models import SavedTrip

class SavedTripView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all saved trips for the authenticated user"""
        trips = SavedTrip.objects.filter(user=request.user).order_by('-created_at')
        data = [
            {
                "id": trip.id,
                "title": trip.title,
                "itinerary_json": trip.itinerary_json,
                "created_at": trip.created_at
            } for trip in trips
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Save a new trip to the user's profile"""
        title = request.data.get("title")
        itinerary_json = request.data.get("itinerary_json")
        
        if not title or not itinerary_json:
            return Response({"error": "Title and itinerary JSON are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        trip = SavedTrip.objects.create(
            user=request.user,
            title=title,
            itinerary_json=itinerary_json
        )
        return Response({"message": "Trip saved successfully", "id": trip.id}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Delete a saved trip"""
        try:
            trip = SavedTrip.objects.get(pk=pk, user=request.user)
            trip.delete()
            return Response({"message": "Trip deleted successfully"}, status=status.HTTP_200_OK)
        except SavedTrip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

class ItineraryAgentView(APIView):
    """
    POST /api/v1/plan/
    Body: { "preferences": "I want a 7 day honeymoon in the hill country" }
    """
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
