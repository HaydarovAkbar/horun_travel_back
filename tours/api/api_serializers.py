from rest_framework import serializers
from tours.models import (
    TourCategory, TourTag, Tour, TourImage, TourVideo, ItineraryDay, TourStop, TourDeparture
)
from locations.api.api_serializers import CountrySerializer, CitySerializer

class TourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory
        fields = ["id", "name", "slug"]

class TourTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourTag
        fields = ["id", "name", "slug"]

class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ["image", "alt", "is_cover", "order"]

class TourVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourVideo
        fields = ["provider", "url", "title", "order"]

class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        fields = ["day_number", "title", "description", "image"]

class TourStopSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    class Meta:
        model = TourStop
        fields = ["order", "country", "city", "stay_nights", "note"]

class TourDepartureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourDeparture
        fields = ["start_date", "end_date", "seats_total", "seats_left"]

class TourListSerializer(serializers.ModelSerializer):
    category = TourCategorySerializer(read_only=True)
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ["id", "slug", "title", "category", "days", "base_price", "currency", 'short_description',
                  "discount_percent", "discount_amount", "price_after_discount", "is_featured", "cover"]

    def get_cover(self, obj):
        img = next((im for im in obj.images.all() if im.is_cover), None) or obj.images.first()
        return img.image.url if img else None

class TourDetailSerializer(serializers.ModelSerializer):
    category = TourCategorySerializer(read_only=True)
    tags = TourTagSerializer(read_only=True, many=True)
    images = TourImageSerializer(read_only=True, many=True)
    videos = TourVideoSerializer(read_only=True, many=True)
    itinerary = ItineraryDaySerializer(read_only=True, many=True)
    route = TourStopSerializer(read_only=True, many=True)
    departures = TourDepartureSerializer(read_only=True, many=True)

    class Meta:
        model = Tour
        fields = [
            "id", "slug", "title", "short_description", "long_description",
            "category", "tags", "days",
            "base_price", "currency", "discount_percent", "discount_amount", "price_after_discount",
            "difficulty", "is_featured",
            "images", "videos", "itinerary", "route", "departures",
            "meta_title", "meta_description",
        ]
