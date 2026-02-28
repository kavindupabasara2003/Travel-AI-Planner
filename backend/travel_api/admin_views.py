from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from .models import SavedTrip, ItineraryCache

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        user_count = User.objects.count()
        trip_count = SavedTrip.objects.count()
        cache_count = ItineraryCache.objects.count()
        
        return Response({
            "total_users": user_count,
            "total_trips": trip_count,
            "total_cached_queries": cache_count
        }, status=status.HTTP_200_OK)

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = [
            {
                "id": u.id,
                "email": u.email,
                "is_staff": u.is_staff,
                "date_joined": u.date_joined,
                "last_login": u.last_login
            } for u in users
        ]
        return Response(data, status=status.HTTP_200_OK)

class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user.is_superuser:
                return Response({"error": "Cannot delete superuser"}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class AdminTripListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        trips = SavedTrip.objects.select_related('user').all().order_by('-created_at')
        data = [
            {
                "id": t.id,
                "user_email": t.user.email,
                "title": t.title,
                "created_at": t.created_at,
                "itinerary_json": t.itinerary_json
            } for t in trips
        ]
        return Response(data, status=status.HTTP_200_OK)

class AdminTripDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            trip = SavedTrip.objects.get(pk=pk)
            trip.delete()
            return Response({"message": "Trip deleted successfully"}, status=status.HTTP_200_OK)
        except SavedTrip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

class AdminCacheListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        caches = ItineraryCache.objects.all().order_by('-created_at')
        data = [
            {
                "id": c.id,
                "query_text": c.query_text,
                "created_at": c.created_at
            } for c in caches
        ]
        return Response(data, status=status.HTTP_200_OK)
        
    def delete(self, request):
        ItineraryCache.objects.all().delete()
        return Response({"message": "Cache cleared successfully"}, status=status.HTTP_200_OK)

class AdminCacheDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            cache = ItineraryCache.objects.get(pk=pk)
            cache.delete()
            return Response({"message": "Cache entry deleted successfully"}, status=status.HTTP_200_OK)
        except ItineraryCache.DoesNotExist:
            return Response({"error": "Cache entry not found"}, status=status.HTTP_404_NOT_FOUND)
