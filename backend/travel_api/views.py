from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services.llama_service import LLaMAService
from .services.trip_assistant import TripAssistantService
from .models import SavedTrip, AttractionAspectScore, ConversationHistory

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


class AspectScoreView(APIView):
    """
    GET /api/v1/aspects/?city=Kandy&sort_by=scenery
    Returns ABSA scores for attractions, optionally filtered by city and sorted by any aspect.
    """
    permission_classes = [AllowAny]

    VALID_SORT_FIELDS = {
        "scenery", "cleanliness", "crowd_level", "value_for_money",
        "accessibility", "safety", "food_quality", "cultural_significance",
    }

    def get(self, request):
        qs = AttractionAspectScore.objects.all()

        city = request.query_params.get("city")
        if city:
            qs = qs.filter(located_city__icontains=city)

        loc_type = request.query_params.get("type")
        if loc_type:
            qs = qs.filter(location_type__icontains=loc_type)

        sort_by = request.query_params.get("sort_by", "scenery")
        if sort_by not in self.VALID_SORT_FIELDS:
            sort_by = "scenery"
        qs = qs.order_by(f"-{sort_by}")

        names = request.query_params.get("names")
        if names:
            name_list = [n.strip() for n in names.split(",")]
            qs = AttractionAspectScore.objects.filter(attraction_name__in=name_list)

        data = [
            {
                "attraction_name": a.attraction_name,
                "location_type": a.location_type,
                "located_city": a.located_city,
                "scores": {
                    "scenery": a.scenery,
                    "cleanliness": a.cleanliness,
                    "crowd_level": a.crowd_level,
                    "value_for_money": a.value_for_money,
                    "accessibility": a.accessibility,
                    "safety": a.safety,
                    "food_quality": a.food_quality,
                    "cultural_significance": a.cultural_significance,
                },
            }
            for a in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


class ConversationHistoryView(APIView):
    """
    GET  /api/v1/history/  — fetch last N messages for the authenticated user
    POST /api/v1/history/  — save a new message
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        messages = ConversationHistory.objects.filter(
            user=request.user
        ).order_by("-created_at")[:limit]
        data = [
            {"role": m.role, "content": m.content, "created_at": m.created_at}
            for m in reversed(list(messages))
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        role = request.data.get("role")
        content = request.data.get("content")
        if role not in ("user", "assistant") or not content:
            return Response(
                {"error": "role (user|assistant) and content are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        msg = ConversationHistory.objects.create(
            user=request.user, role=role, content=content
        )
        return Response({"id": msg.id}, status=status.HTTP_201_CREATED)


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
        itinerary_date = request.data.get("itinerary_date")

        if not location or not query:
             return Response({"error": "Location and Query are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assistant = TripAssistantService()
            advice = assistant.get_advice(query, location, lat, lon, activity, description, theme, itinerary_date)

            return Response({"advice": advice}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MultiItineraryView(APIView):
    """
    POST /api/v1/plan/multi/
    Body: { "preferences": { duration, startLocation, groupSize, tripType } }
    Returns list of 3 itinerary variations.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = request.data.get("preferences")
        if not preferences:
            return Response({"error": "preferences required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agent = LLaMAService()
            variations = agent.generate_multi_itinerary(preferences)
            return Response({"variations": variations}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrowdPredictView(APIView):
    """
    GET /api/v1/crowd/?date=2026-04-25
    Returns ML crowd prediction for a given date.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            from datetime import date
            date_str = date.today().isoformat()

        try:
            from .services.crowd_predictor import CrowdPredictor
            predictor = CrowdPredictor()
            result = predictor.predict(date_str)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WeatherForecastView(APIView):
    """
    GET /api/v1/forecast/?cities=Colombo,Kandy,Ella
    Returns 7-day forecasts for requested cities.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cities_param = request.query_params.get("cities", "")
        city_list = [c.strip() for c in cities_param.split(",") if c.strip()]

        if not city_list:
            return Response({"error": "Provide ?cities=City1,City2"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .services.weather_forecast import WeatherForecastService
            svc = WeatherForecastService()
            data = {}
            for city in city_list:
                data[city] = svc.get_forecast(city)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TravelTwinView(APIView):
    """
    POST /api/v1/twins/
    Body: { "preferences": "5 day beach trip from Galle" }
    Returns top-3 similar cached itineraries via pgvector.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = request.data.get("preferences", "")
        if not preferences:
            return Response({"error": "preferences required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .services.llama_service import LLaMAService
            from .services.itinerary_store import ItineraryStore
            from .models import ItineraryCache
            from pgvector.django import CosineDistance

            agent = LLaMAService()
            embedding = agent.get_embedding(preferences)
            if not embedding:
                return Response({"error": "Could not generate embedding"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            matches = (
                ItineraryCache.objects
                .annotate(distance=CosineDistance("embedding", embedding))
                .order_by("distance")[:5]
            )

            results = []
            for m in matches:
                if m.distance > 0.01:  # exclude near-exact matches
                    itinerary = m.itinerary_json
                    results.append({
                        "similarity": round((1 - m.distance) * 100, 1),
                        "query": m.query_text,
                        "title": itinerary.get("title", ""),
                        "total_days": itinerary.get("total_days", ""),
                        "trip_theme": itinerary.get("trip_theme", ""),
                        "summary": itinerary.get("summary", ""),
                        "itinerary": itinerary,
                    })
                if len(results) >= 3:
                    break

            return Response({"twins": results}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PersonaView(APIView):
    """
    GET /api/v1/persona/
    Returns the authenticated user's travel persona based on saved trip themes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from .services.persona_engine import PersonaEngine
            engine = PersonaEngine()
            persona = engine.get_persona(request.user)
            return Response(persona, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
