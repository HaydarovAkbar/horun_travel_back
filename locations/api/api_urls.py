from rest_framework.routers import DefaultRouter
from .api_views import CountryViewSet, CityViewSet

router = DefaultRouter()
router.register("countries", CountryViewSet, basename="countries")
router.register("cities", CityViewSet, basename="cities")

urlpatterns = router.urls
