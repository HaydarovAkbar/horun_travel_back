from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    SiteSettings, ContactChannel, SocialLink,
    Location, WorkingHour,
)
from locations.models import Country, City


# --------- Umumiy actions ---------
@admin.action(description="Faollashtirish")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True, is_deleted=False)

@admin.action(description="Faolsizlantirish")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description="Soft-delete (o‘chirish)")
def soft_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True, is_active=False)

@admin.action(description="Tiklash (soft-delete dan)")
def restore(modeladmin, request, queryset):
    queryset.update(is_deleted=False, is_active=True)


# --------- Inline’lar ---------
class ContactChannelInline(admin.TabularInline):
    model = ContactChannel
    extra = 0
    fields = ("order", "type", "label", "value", "is_primary", "is_active")
    ordering = ("order", "id")
    classes = ("collapse",)

class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    fields = ("order", "provider", "label", "url", "is_active")
    ordering = ("order", "id")
    classes = ("collapse",)

class LocationInline(admin.TabularInline):
    """
    SiteSettings ichida lokatsiyalarni ko‘rsatamiz.
    Ish vaqtlari (WorkingHour) nested-inline bo‘la olmaydi, shuning uchun
    `show_change_link=True` bilan alohida sahifasiga o‘tamiz.
    """
    model = Location
    extra = 0
    fields = ("order", "name", "country", "city", "address_line", "is_primary", "is_active")
    autocomplete_fields = ("country", "city")
    show_change_link = True
    ordering = ("order", "id")
    classes = ("collapse",)


class WorkingHourInline(admin.TabularInline):
    model = WorkingHour
    extra = 0
    fields = ("weekday", "closed", "open_time", "close_time", "order", "is_active")
    ordering = ("order", "weekday")
    classes = ("collapse",)


# --------- SiteSettings (singleton) ---------
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [ContactChannelInline, SocialLinkInline, LocationInline]

    list_display = ("__str__", "logo_preview", "primary_phone", "primary_email", "updated_at")
    search_fields = ("^org_name", "^primary_phone", "^primary_email")
    readonly_fields = ("created_at", "updated_at", "logo_preview", "favicon_preview")
    actions = [make_active, make_inactive, soft_delete, restore]
    save_on_top = True

    fieldsets = (
        ("Asosiy ma’lumotlar", {
            "fields": ("org_name", "slogan", "is_active")
        }),
        ("Brending (media)", {
            "fields": ("logo", "logo_dark", "favicon", "logo_preview", "favicon_preview"),
        }),
        ("Aloqa", {
            "fields": ("primary_phone", "primary_email"),
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
        ("Texnik", {
            "fields": ("singleton_key", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    # Singleton xatti-harakatlari: bitta yozuvdan ko‘piga ruxsat bermaslik
    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    # List sahifasidan to‘g‘ridan-to‘g‘ri o‘sha bitta yozuvga o‘tkazish (UX uchun)
    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.get_solo()
        return HttpResponseRedirect(
            reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=(obj.pk,))
        )

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;">', obj.logo.url)
        return "—"

    @admin.display(description="Favicon")
    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html('<img src="{}" style="height:24px;border-radius:4px;">', obj.favicon.url)
        return "—"


# --------- Location ---------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = [WorkingHourInline]

    list_display = ("name_or_city", "country", "city", "address_line", "is_primary", "order", "is_active", "updated_at")
    list_filter = ("is_active", "is_primary", "country")
    search_fields = ("^name", "city__name", "address_line", "postal_code", "place_id")
    autocomplete_fields = ("settings", "country", "city")
    list_select_related = ("country", "city", "settings")
    ordering = ("order", "id")
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Asosiy", {
            "fields": ("settings", "name", "is_primary", "order", "is_active"),
        }),
        ("Joylashuv", {
            "fields": ("country", "city", "address_line", "postal_code"),
        }),
        ("Xarita", {
            "fields": ("lat", "lng", "map_embed_url", "place_id"),
            "classes": ("collapse",)
        }),
        ("Texnik", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    @admin.display(description="Nom")
    def name_or_city(self, obj):
        return obj.name or (obj.city.name if obj.city_id else obj.country.name)


# --------- ContactChannel (alohida boshqarish ham qulay bo‘lsin) ---------
@admin.register(ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ("type", "label", "value", "is_primary", "order", "is_active", "updated_at")
    list_filter = ("type", "is_primary", "is_active")
    search_fields = ("^label", "^value")
    autocomplete_fields = ("settings",)
    ordering = ("order", "id")
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")


# --------- SocialLink ---------
@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("provider", "label", "url", "order", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
    search_fields = ("^label", "^url")
    autocomplete_fields = ("settings",)
    ordering = ("order", "id")
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")


# --------- WorkingHour (ixtiyoriy: alohida ro‘yxatda ko‘rish uchun) ---------
@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ("location", "weekday", "closed", "open_time", "close_time", "order", "is_active", "updated_at")
    list_filter = ("weekday", "closed", "is_active", "location__country")
    search_fields = ("location__name", "location__city__name", "location__address_line")
    autocomplete_fields = ("location",)
    ordering = ("location", "weekday", "order", "id")
    actions = [make_active, make_inactive, soft_delete, restore]
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at")
