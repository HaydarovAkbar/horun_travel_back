from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from common.models import BaseModel
from locations.models import Country, City


class TourCategory(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class TourTag(BaseModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tour(BaseModel):
    STATUS = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )
    DIFFICULTY = (
        ("easy", "Easy"),
        ("moderate", "Moderate"),
        ("hard", "Hard"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(TourCategory, on_delete=models.PROTECT, related_name="tours")
    tags = models.ManyToManyField(TourTag, blank=True, related_name="tours")

    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)

    days = models.PositiveSmallIntegerField(help_text="Necha kunlik tur")
    min_group = models.PositiveSmallIntegerField(default=1)
    max_group = models.PositiveSmallIntegerField(default=20)

    base_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")  # USD/EUR/UZS...
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="0–100 oralig‘i, foiz"
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Valyutadagi chegirma (masalan 50.00 USD)"
    )

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default="easy")
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS, default="published")

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    # M2M via through (marshrut uchun)
    stops = models.ManyToManyField(City, through="TourStop", related_name="tours", blank=True)

    class Meta:
        ordering = ["order", '-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        # Discount validatsiya
        if self.discount_percent and (self.discount_percent < 0 or self.discount_percent > 100):
            raise ValidationError({"discount_percent": "0 va 100 oralig‘ida bo‘lishi kerak."})

        if self.discount_percent and self.discount_amount:
            # Ikkalasi birdaniga bo‘lishi yaxshi emas (bizdan tanlashni xohlaymiz)
            raise ValidationError("Yoki foizli, yoki summali chegirma — ikkalasini birga bermang.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    @property
    def price_after_discount(self):
        """Chegirmadan keyingi narx (agar bor bo‘lsa)."""
        if self.base_price is None:
            return None
        price = self.base_price
        if self.discount_percent:
            price = price * (1 - (self.discount_percent / 100))
        elif self.discount_amount:
            price = max(price - self.discount_amount, 0)
        return price


class TourStop(BaseModel):
    """
    Marshrutdagi tartibli nuqta.
    - country: majburiy emas, city bo‘lsa country avtomatik city.country ga teng bo‘ladi
    - city: ixtiyoriy (ba’zi marshrutlar shahar emas, davlat darajasida bo‘lishi mumkin)
    """
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="tour_stops")
    order = models.PositiveIntegerField(default=0, db_index=True)

    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True, related_name="tour_stops")
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True, related_name="tour_stops")

    stay_nights = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Necha kecha shu joyda")
    note = models.CharField(max_length=255, blank=True, help_text="Qisqa izoh (ixtiyoriy)")

    class Meta:
        ordering = ["order", "id"]
        unique_together = (("tour", "order"),)

    def __str__(self):
        where = self.city.name if self.city else (self.country.name if self.country else "—")
        return f"{self.tour.title} → {self.order}. {where}"

    def clean(self):
        if not self.country and not self.city:
            raise ValidationError("Kamida country yoki city kiritilishi kerak.")
        if self.city and self.country and self.city.country_id != self.country_id:
            raise ValidationError("City va Country mos kelmadi (city.country != country).")

    def save(self, *args, **kwargs):
        # city bo‘lsa, country bo‘sh bo‘lsa — avtomatik to‘ldiramiz
        if self.city and not self.country:
            self.country = self.city.country
        super().save(*args, **kwargs)


class ItineraryDay(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="itinerary")
    day_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="tours/itinerary/", blank=True)

    class Meta:
        ordering = ["day_number"]
        unique_together = (("tour", "day_number"),)

    def __str__(self):
        return f"{self.tour.title} / Day {self.day_number}"


class TourImage(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="tours/images/")
    alt = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.alt or self.image.name


class TourVideo(BaseModel):
    PROVIDERS = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
        ("file", "File/Direct"),
    )
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="videos")
    provider = models.CharField(max_length=10, choices=PROVIDERS, default="youtube")
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or self.url


# (ixtiyoriy) Belgilangan boshlanishlar/kvotalar – agar “fixed departure” tur bo‘lsa foydali
class TourDeparture(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="departures")
    start_date = models.DateField()
    end_date = models.DateField()
    seats_total = models.PositiveSmallIntegerField(null=True, blank=True)
    seats_left = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.tour.title} [{self.start_date} → {self.end_date}]"
