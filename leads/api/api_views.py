from rest_framework import generics, throttling
from leads.models import Application, ContactMessage
from .api_serializers import ApplicationCreateSerializer, ContactMessageCreateSerializer

class ApplicationsThrottle(throttling.AnonRateThrottle):
    scope = "applications"

class ContactsThrottle(throttling.AnonRateThrottle):
    scope = "contacts"

class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationCreateSerializer
    throttle_classes = [ApplicationsThrottle]

class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageCreateSerializer
    throttle_classes = [ContactsThrottle]
