from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField

class ItineraryCache(models.Model):
    query_text = models.TextField(help_text="The exact query string used")
    embedding = VectorField(dimensions=768, help_text="Nomic embed-text embedding vector")
    itinerary_json = models.JSONField(help_text="The generated itinerary response")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cache for: {self.query_text[:50]}"

class SavedTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_trips')
    title = models.CharField(max_length=255, help_text="Title of the trip (e.g. 7 Days in Colombo)")
    itinerary_json = models.JSONField(help_text="The full structured trip data")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Trip: {self.title}"
