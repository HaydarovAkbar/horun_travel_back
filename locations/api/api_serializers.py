from rest_framework import serializers
from locations.models import Country, City

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "iso2", "iso3", "phone_code", "region", "subregion"]

class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    class Meta:
        model = City
        fields = ["id", "name", "ascii_name", "country", "admin1", "tz", "population", "lat", "lng", "geoname_id"]
