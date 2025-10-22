from rest_framework import serializers
from siteinfo.models import SiteSettings, ContactChannel, SocialLink, Location, WorkingHour, AboutPage, AboutSection, ContactPage
from locations.api.api_serializers import CountrySerializer, CitySerializer

class ContactChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactChannel
        fields = ["type", "label", "value", "is_primary", "order"]

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ["provider", "label", "url", "order"]

class WorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHour
        fields = ["weekday", "closed", "open_time", "close_time"]

class LocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    hours = WorkingHourSerializer(many=True, read_only=True)
    class Meta:
        model = Location
        fields = ["name", "country", "city", "address_line", "lat", "lng", "map_embed_url", "is_primary", "order", "hours"]

class SiteSettingsSerializer(serializers.ModelSerializer):
    contacts = ContactChannelSerializer(many=True, read_only=True)
    socials  = SocialLinkSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    class Meta:
        model = SiteSettings
        fields = [
            "org_name", "slogan", "logo", "logo_dark", "favicon",
            "primary_phone", "primary_email",
            "meta_title", "meta_description",
            "contacts", "socials", "locations",
        ]

class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = ["order", "title", "body", "image"]

class AboutPageSerializer(serializers.ModelSerializer):
    sections = AboutSectionSerializer(many=True, read_only=True)
    class Meta:
        model = AboutPage
        fields = ["hero_title", "hero_subtitle", "hero_image", "video_url", "meta_title", "meta_description", "sections"]

class ContactPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPage
        fields = ["hero_title", "hero_subtitle", "intro_html", "meta_title", "meta_description"]
