from django.db import models
from common.models import BaseModel

class Country(BaseModel):
    # ISO va statistik identifikatorlar
    name = models.CharField(max_length=128, db_index=True)         # English yoki primary nom
    iso2 = models.CharField(max_length=2, unique=True)             # ISO 3166-1 alpha-2 (UZ, TR, etc.)
    iso3 = models.CharField(max_length=3, unique=True, blank=True) # ISO 3166-1 alpha-3 (UZB, TUR)
    m49 = models.PositiveIntegerField(null=True, blank=True)       # UN M49 numeric
    numeric = models.PositiveIntegerField(null=True, blank=True)   # ISO 3166-1 numeric (ko‘pincha M49 bilan mos)
    phone_code = models.CharField(max_length=8, blank=True)        # E.164 (+998, +90 …) — ko‘p hududli davlatlar uchun ko‘p qiymat saqlashga kerak bo‘lsa JSONField ham mumkin
    region = models.CharField(max_length=64, blank=True)           # UN region: Europe, Asia, …
    subregion = models.CharField(max_length=64, blank=True)        # UN subregion: Central Asia, …
    capital = models.CharField(max_length=128, blank=True)
    currency = models.CharField(max_length=3, blank=True)          # UZS, TRY, …
    tz_primary = models.CharField(max_length=64, blank=True)       # Asia/Tashkent (asosiy)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.iso2})"


class City(BaseModel):
    name = models.CharField(max_length=150, db_index=True)
    ascii_name = models.CharField(max_length=150, blank=True)      # qidiruv uchun foydali
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")
    admin1 = models.CharField(max_length=150, blank=True)          # viloyat/shtat nomi (GeoNames admin1)
    admin2 = models.CharField(max_length=150, blank=True)          # tuman/okrug
    tz = models.CharField(max_length=64, blank=True)               # IANA tz (Asia/Tashkent)
    population = models.BigIntegerField(null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    geoname_id = models.BigIntegerField(null=True, blank=True, unique=True)  # GeoNames ID

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["country", "name"]),
            models.Index(fields=["-population"]),
        ]
        ordering = ["-population", "name"]

    def __str__(self):
        return f"{self.name}, {self.country.iso2}"
