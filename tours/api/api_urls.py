from rest_framework.routers import DefaultRouter
from .api_views import TourViewSet, TourCategoryViewSet, TourTagViewSet

router = DefaultRouter()
router.register("list", TourViewSet, basename="tours")  # /api/v1/tours/list/
router.register("categories", TourCategoryViewSet, basename="tour-categories")
router.register("tags", TourTagViewSet, basename="tour-tags")

urlpatterns = router.urls
