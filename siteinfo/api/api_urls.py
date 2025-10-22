from django.urls import path
from .api_views import SiteSettingsView, AboutPageView, ContactPageView

urlpatterns = [
    path("settings/", SiteSettingsView.as_view()),
    path("about/", AboutPageView.as_view()),
    path("contact/", ContactPageView.as_view()),
]
