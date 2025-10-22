from django.urls import path, include

urlpatterns = [
    path("tours/", include("tours.api.api_urls")),
    path("site/", include("siteinfo.api.api_urls")),
    path("leads/", include("leads.api.api_urls")),
    path("locations/", include("locations.api.api_urls")),
]