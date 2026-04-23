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

class AttractionAspectScore(models.Model):
    """Aspect-based sentiment scores for Sri Lankan attractions (ABSA Feature)."""
    attraction_name = models.CharField(max_length=255, unique=True)
    location_type = models.CharField(max_length=100, blank=True)
    located_city = models.CharField(max_length=255, blank=True)
    # Eight aspect dimensions, each 0.0 – 1.0
    scenery = models.FloatField(default=0.5)
    cleanliness = models.FloatField(default=0.5)
    crowd_level = models.FloatField(default=0.5)
    value_for_money = models.FloatField(default=0.5)
    accessibility = models.FloatField(default=0.5)
    safety = models.FloatField(default=0.5)
    food_quality = models.FloatField(default=0.5)
    cultural_significance = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aspects: {self.attraction_name}"

    class Meta:
        ordering = ['attraction_name']

class ConversationHistory(models.Model):
    """Persisted chat history for cross-session conversational memory (Feature 13)."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_history')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} [{self.role}]: {self.content[:50]}"

    class Meta:
        ordering = ['created_at']
