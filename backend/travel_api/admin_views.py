from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
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


class AdminAnalyticsView(APIView):
    """GET /api/v1/admin/analytics/ — chart data for admin dashboard."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        since = datetime.now() - timedelta(days=30)

        # Trips per day (last 30 days)
        trips_by_day = (
            SavedTrip.objects.filter(created_at__gte=since)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Theme distribution
        theme_dist = {}
        for trip in SavedTrip.objects.all():
            theme = trip.itinerary_json.get("trip_theme", "Unknown") if isinstance(trip.itinerary_json, dict) else "Unknown"
            theme_dist[theme] = theme_dist.get(theme, 0) + 1

        # Popular start cities
        city_dist = {}
        for trip in SavedTrip.objects.all():
            if isinstance(trip.itinerary_json, dict):
                days = trip.itinerary_json.get("days", [])
                if days:
                    city = days[0].get("location", "Unknown")
                    city_dist[city] = city_dist.get(city, 0) + 1
        top_cities = sorted(city_dist.items(), key=lambda x: x[1], reverse=True)[:8]

        total_requests = ItineraryCache.objects.count()

        return Response({
            "trips_by_day": [{"date": str(r["date"]), "count": r["count"]} for r in trips_by_day],
            "theme_distribution": [{"theme": k, "count": v} for k, v in theme_dist.items()],
            "popular_start_cities": [{"city": c, "count": n} for c, n in top_cities],
            "cache_total": total_requests,
        }, status=status.HTTP_200_OK)
