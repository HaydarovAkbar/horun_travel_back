# tours/admin.py
from django.contrib import admin
from django import forms
from django.db.models import Prefetch
from django.utils.html import format_html

from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import (
    TourCategory, TourTag, Tour,
    TourStop, ItineraryDay, TourImage, TourVideo, TourDeparture
)

# ---------- Actions ----------
@admin.action(description="Publish selected")
def make_published(modeladmin, request, queryset):
    queryset.update(status="published", is_active=True, is_deleted=False)

@admin.action(description="Archive selected")
def make_archived(modeladmin, request, queryset):
    queryset.update(status="archived")

@admin.action(description="Mark as Featured")
def set_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)

@admin.action(description="Unmark Featured")
def unset_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)

# ---------- Filterlar ----------
class HasDiscountFilter(admin.SimpleListFilter):
    title = "Chegirma"
    parameter_name = "has_discount"
    def lookups(self, request, model_admin):
        return (("yes", "Bor"), ("no", "Yo‘q"))
    def queryset(self, request, qs):
        v = self.value()
        if v == "yes":
            return qs.filter(discount_percent__isnull=False) | qs.filter(discount_amount__isnull=False)
        if v == "no":
            return qs.filter(discount_percent__isnull=True, discount_amount__isnull=True)
        return qs

class HasCoverFilter(admin.SimpleListFilter):
    title = "Cover rasm"
    parameter_name = "has_cover"
    def lookups(self, request, model_admin):
        return (("yes", "Bor"), ("no", "Yo‘q"))
    def queryset(self, request, qs):
        v = self.value()
        if v == "yes":
            return qs.filter(images__is_cover=True).distinct()
        if v == "no":
            return qs.exclude(images__is_cover=True).distinct()
        return qs

# ---------- CKEditor helper ----------
LANGS = ("uz", "ru", "en")
def ck_widgets(*field_bases, cfg="long"):
    widgets = {}
    for base in field_bases:
        for lang in LANGS:
            widgets[f"{base}_{lang}"] = CKEditor5Widget(config_name=cfg)
    return widgets

# ---------- Forms (CKEditor 5 qo‘llash) ----------
class TourAdminForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = "__all__"
        widgets = {
            **ck_widgets("title", "short_description", "meta_title", cfg="default"),
            **ck_widgets("long_description", "meta_description", cfg="long"),
        }

class ItineraryDayInlineForm(forms.ModelForm):
    class Meta:
        model = ItineraryDay
        fields = "__all__"
        widgets = {
            **ck_widgets("title", cfg="default"),
            **ck_widgets("description", cfg="long"),
        }

# ---------- Inlines ----------
class TourStopInline(admin.TabularInline):
    model = TourStop
    extra = 0
    ordering = ("order", "id")
    fields = ("order", "country", "city", "stay_nights", "note", "is_active")
    autocomplete_fields = ("country", "city")

class ItineraryDayInline(TranslationTabularInline):
    model = ItineraryDay
    form = ItineraryDayInlineForm
    extra = 0
    ordering = ("day_number",)
    fields = ("day_number", "title", "description", "image", "is_active")
    classes = ("collapse",)

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 0
    ordering = ("order", "id")
    fields = ("image", "alt", "is_cover", "order", "is_active")
    classes = ("collapse",)

class TourVideoInline(admin.TabularInline):
    model = TourVideo
    extra = 0
    ordering = ("order", "id")
    fields = ("provider", "url", "title", "order", "is_active")
    classes = ("collapse",)

class TourDepartureInline(admin.TabularInline):
    model = TourDeparture
    extra = 0
    ordering = ("start_date",)
    fields = ("start_date", "end_date", "seats_total", "seats_left", "is_active")
    classes = ("collapse",)

# ---------- Category & Tag ----------
@admin.register(TourCategory)
class TourCategoryAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active", "updated_at")
    search_fields = ("^name", "^slug")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

@admin.register(TourTag)
class TourTagAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "updated_at")
    search_fields = ("^name", "^slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

# ---------- Tour (Tabbed + CKEditor) ----------
@admin.register(Tour)
class TourAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    form = TourAdminForm
    inlines = [TourStopInline, ItineraryDayInline, TourImageInline, TourVideoInline, TourDepartureInline]

    # tezlik: select_related(category), prefetch(images cover)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category").prefetch_related(
            Prefetch("images", queryset=TourImage.objects.order_by("order", "id"))
        )

    list_display = ("cover_thumb", "title", "category", "days", "group_range",
                    "price_display", "status", "is_featured", "order", "updated_at")
    list_display_links = ("cover_thumb", "title")
    list_editable = ("is_featured", "order")
    list_filter = ("status", "is_featured", "category", "difficulty", HasDiscountFilter, HasCoverFilter)
    search_fields = ("^title", "^slug", "short_description", "long_description")
    autocomplete_fields = ("category", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("order", "-created_at")
    actions = [make_published, make_archived, set_featured, unset_featured]
    list_per_page = 50
    save_on_top = True

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        img = next((im for im in obj.images.all() if im.is_cover), None) or (obj.images.all()[0] if obj.images.all() else None)
        if not img:
            return "—"
        try:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;object-fit:cover;">', img.image.url)
        except Exception:
            return "—"

    @admin.display(description="Guruh")
    def group_range(self, obj):
        return f"{obj.min_group}–{obj.max_group}"

    @admin.display(description="Narx", ordering="base_price")
    def price_display(self, obj):
        if obj.base_price is None:
            return "—"
        if obj.discount_percent or obj.discount_amount:
            return format_html(
                '<span style="text-decoration:line-through;opacity:.6;">{:.2f} {}</span>&nbsp;<b>{:.2f} {}</b>',
                obj.base_price, obj.currency,
                (obj.price_after_discount or obj.base_price), obj.currency
            )
        return f"{obj.base_price:.2f} {obj.currency}"

# ---------- Qo'shimcha adminlar (ixtiyoriy, foydali) ----------
@admin.register(TourStop)
class TourStopAdmin(admin.ModelAdmin):
    list_display = ("tour", "order", "country", "city", "stay_nights", "note", "is_active", "updated_at")
    list_filter = ("tour", "country")
    search_fields = ("tour__title", "country__name", "city__name", "note")
    autocomplete_fields = ("tour", "country", "city")
    ordering = ("tour", "order")
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")

@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ("tour", "day_number", "title", "is_active", "updated_at")
    list_filter = ("tour",)
    search_fields = ("tour__title", "title", "description")
    autocomplete_fields = ("tour",)
    ordering = ("tour", "day_number")
    list_per_page = 50

@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ('id', "tour", "thumb", "alt", "is_cover", "order", "is_active", "updated_at")
    list_filter = ("tour", "is_cover")
    search_fields = ("tour__title", "alt")
    autocomplete_fields = ("tour",)
    ordering = ("tour", "order", "id")
    list_per_page = 50
    @admin.display(description="Preview")
    def thumb(self, obj):
        try:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;">', obj.image.url)
        except Exception:
            return "—"

@admin.register(TourVideo)
class TourVideoAdmin(admin.ModelAdmin):
    list_display = ("tour", "provider", "title", "url", "order", "is_active", "updated_at")
    list_filter = ("tour", "provider")
    search_fields = ("tour__title", "title", "url")
    autocomplete_fields = ("tour",)
    ordering = ("tour", "order", "id")
    list_per_page = 50

@admin.register(TourDeparture)
class TourDepartureAdmin(admin.ModelAdmin):
    list_display = ("tour", "start_date", "end_date", "seats_total", "seats_left", "is_active", "updated_at")
    list_filter = ("tour",)
    search_fields = ("tour__title",)
    autocomplete_fields = ("tour",)
    ordering = ("tour", "start_date")
    list_per_page = 50
