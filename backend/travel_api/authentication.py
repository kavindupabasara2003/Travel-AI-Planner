import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header
from travel_ai_backend.mongo_setup import MongoDBClient
from bson.objectid import ObjectId

class MongoAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # --- SUPERVISOR BYPASS MODE ---
        # Allow instant access for the supervisor demo
        demo_user_payload = {
            'user_id': 'supervisor_demo_123',
            'email': 'kavindu.pabasaraz12@gmail.com',
            'role': 'service_role'
        }
        return (SimpleUser('supervisor_demo_123', demo_user_payload), "mock_token")
        
        # Original Logic Below (Commented Out)
        # auth = get_authorization_header(request).split()
        # if not auth or auth[0].lower() != b'bearer': return None
        # ... (rest of logic)

class SimpleUser:
    def __init__(self, user_id, payload):
        self.id = user_id
        self.payload = payload
        self.is_authenticated = True
        self.email = payload.get('email', 'guest@example.com')

    def __str__(self):
        return self.email

