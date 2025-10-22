from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch

from tours.models import Tour, TourCategory, TourTag, TourImage, TourStop
from .api_serializers import (
    TourListSerializer, TourDetailSerializer, TourCategorySerializer, TourTagSerializer, TourDepartureSerializer
)
from .api_filters import TourFilter


class TourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Tour.objects.filter(is_active=True, is_deleted=False)
        .select_related("category")
        .prefetch_related(
            Prefetch("images", queryset=TourImage.objects.order_by("order", "id")),
            Prefetch("tour_stops",  # <-- THROUGH yozuvlarni olamiz
                     queryset=TourStop.objects.select_related("country", "city")
                                               .order_by("order", "id")),
            "tags",
            "itinerary",   # <-- related_name ItineraryDay uchun
            "videos",
            "departures",
        )
        .distinct()
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TourFilter
    search_fields = ["^title", "short_description", "long_description", "tags__name", "category__name"]
    ordering_fields = ["price_after_discount", "base_price", "days", "created_at", "order"]
    ordering = ["order", "-created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return TourListSerializer
        return TourDetailSerializer


class TourCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TourCategory.objects.filter(is_active=True)
    serializer_class = TourCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["^name", "^slug"]
    ordering_fields = ["order", "name"]
    ordering = ["order", "name"]


class TourTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TourTag.objects.filter(is_active=True)
    serializer_class = TourTagSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["^name", "^slug"]
    ordering_fields = ["name"]
    ordering = ["name"]
