from django.urls import path
from .api_views import ApplicationCreateView, ContactMessageCreateView

urlpatterns = [
    path("application/", ApplicationCreateView.as_view()),
    path("contact/", ContactMessageCreateView.as_view()),
]
