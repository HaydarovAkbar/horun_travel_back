# locations/admin.py
from django.contrib import admin
from django.db.models import Count
from .models import Country, City


# ---------- Umumiy actions ----------
@admin.action(description="Activate selected")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True, is_deleted=False)

@admin.action(description="Deactivate selected")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description="Soft delete selected")
def soft_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True, is_active=False)

@admin.action(description="Restore (undo soft delete)")
def restore(modeladmin, request, queryset):
    queryset.update(is_deleted=False, is_active=True)


# ---------- Filterlar (chiroyli UX uchun) ----------
class RegionListFilter(admin.SimpleListFilter):
    title = "Region (Country.region)"
    parameter_name = "country_region"

    def lookups(self, request, model_admin):
        qs = Country.objects.exclude(region="").values_list("region", flat=True).distinct().order_by("region")
        return [(r, r) for r in qs]

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        # City admin uchun country__region bo‘yicha filterlash
        if queryset.model is City:
            return queryset.filter(country__region=val)
        # Country admin uchun region bo‘yicha
        return queryset.filter(region=val)


class SubregionListFilter(admin.SimpleListFilter):
    title = "Subregion (Country.subregion)"
    parameter_name = "country_subregion"

    def lookups(self, request, model_admin):
        qs = Country.objects.exclude(subregion="").values_list("subregion", flat=True).distinct().order_by("subregion")
        return [(r, r) for r in qs]

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        if queryset.model is City:
            return queryset.filter(country__subregion=val)
        return queryset.filter(subregion=val)


class PopulationRangeFilter(admin.SimpleListFilter):
    title = "Population"
    parameter_name = "poprange"

    RANGES = (
        ("10m+", "≥ 10,000,000"),
        ("1m-10m", "1,000,000 – 9,999,999"),
        ("100k-1m", "100,000 – 999,999"),
        ("15k-100k", "15,000 – 99,999"),
        ("<15k", "< 15,000"),
        ("null", "Empty/Unknown"),
    )

    def lookups(self, request, model_admin):
        return self.RANGES

    def queryset(self, request, qs):
        v = self.value()
        if not v:
            return qs
        if v == "10m+":
            return qs.filter(population__gte=10_000_000)
        if v == "1m-10m":
            return qs.filter(population__gte=1_000_000, population__lt=10_000_000)
        if v == "100k-1m":
            return qs.filter(population__gte=100_000, population__lt=1_000_000)
        if v == "15k-100k":
            return qs.filter(population__gte=15_000, population__lt=100_000)
        if v == "<15k":
            return qs.filter(population__lt=15_000, population__isnull=False)
        if v == "null":
            return qs.filter(population__isnull=True)


# ---------- Country Admin ----------
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name", "iso2", "iso3", "region", "subregion",
        "currency", "phone_code", "capital", "cities_count",
        "is_active", "created_at", "updated_at",
    )
    list_filter = (
        "is_active",
        RegionListFilter,
        SubregionListFilter,
        # "currency",
    )
    search_fields = (
        "^name", "^iso2", "^iso3",  # prefix-search tezroq
        "^capital", "^currency", "phone_code",
        "m49", "numeric",
    )
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 50
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # cities_count annotatsiyasi: tez ko‘rish uchun
        return qs.annotate(_cities_count=Count("cities"))

    @admin.display(ordering="_cities_count", description="Cities")
    def cities_count(self, obj):
        return obj._cities_count


# ---------- City Admin ----------
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    # Tez sahifa: minimal, lekin foydali ko‘rinish
    list_display = (
        "name", "country", "admin1",
        "population_fmt", "tz",
        "is_active", "updated_at",
    )
    # Katta ro‘yxat uchun:
    list_select_related = ("country",)  # N+1 ni yo‘q qiladi
    list_filter = (
        "is_active",
        RegionListFilter,
        SubregionListFilter,
        # "country",  # tez filtr uchun
        # "tz",
        PopulationRangeFilter,
    )
    # Qidiruv: prefix/^ bilan tezroq (name/ascii_name)
    search_fields = ("^name", "^ascii_name", "admin1", "admin2", "tz", "geoname_id")
    autocomplete_fields = ("country",)  # country tanlashni yengillashtiradi
    ordering = ("-population", "name")
    readonly_fields = ("created_at", "updated_at",)
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 100
    date_hierarchy = "created_at"

    @admin.display(description="Population")
    def population_fmt(self, obj):
        if obj.population is None:
            return "—"
        # minglar bo‘yicha ajratib chiroyli ko‘rsatish
        return f"{obj.population:,}".replace(",", " ")  # no-break space


    # Qo‘shimcha: massiv importdan keyin “faqat active” default ko‘rinishi uchun
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("country")
