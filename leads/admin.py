from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Application, ApplicationAttachment, ContactMessage


# ---------------- Umumiy actions ----------------
@admin.action(description="Faollashtirish")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True, is_deleted=False)

@admin.action(description="Faolsizlantirish")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description="Soft delete (o‘chirish)")
def soft_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True, is_active=False)

@admin.action(description="Tiklash (soft delete dan)")
def restore(modeladmin, request, queryset):
    queryset.update(is_deleted=False, is_active=True)


# --- STATUS actions (Application uchun) ---
@admin.action(description="Holatni: Yangi")
def mark_new(modeladmin, request, queryset):
    queryset.update(status="new")

@admin.action(description="Holatni: Ko‘rib chiqilmoqda")
def mark_in_review(modeladmin, request, queryset):
    queryset.update(status="in_review")

@admin.action(description="Holatni: Aloqa qilindi")
def mark_contacted(modeladmin, request, queryset):
    queryset.update(status="contacted")

@admin.action(description="Holatni: Sotildi / band qilindi")
def mark_won(modeladmin, request, queryset):
    queryset.update(status="won")

@admin.action(description="Holatni: Yo‘qotildi")
def mark_lost(modeladmin, request, queryset):
    queryset.update(status="lost")

@admin.action(description="Holatni: Spam")
def mark_spam(modeladmin, request, queryset):
    queryset.update(status="spam")


# --- STATUS actions (ContactMessage uchun) ---
@admin.action(description="Holatni: Yangi")
def cm_mark_new(modeladmin, request, queryset):
    queryset.update(status="new")

@admin.action(description="Holatni: O‘qildi")
def cm_mark_read(modeladmin, request, queryset):
    queryset.update(status="read")

@admin.action(description="Holatni: Javob berildi")
def cm_mark_answered(modeladmin, request, queryset):
    queryset.update(status="answered")

@admin.action(description="Holatni: Spam")
def cm_mark_spam(modeladmin, request, queryset):
    queryset.update(status="spam")


# ---------------- Inline fayllar ----------------
class ApplicationAttachmentInline(admin.TabularInline):
    model = ApplicationAttachment
    extra = 0
    fields = ("file", "title", "is_active", "created_at")
    readonly_fields = ("created_at",)
    classes = ("collapse",)


# ---------------- FILTERLAR ----------------
class HasBudgetFilter(admin.SimpleListFilter):
    title = "Byudjet"
    parameter_name = "has_budget"

    def lookups(self, request, model_admin):
        return (("yes", "Bor"), ("no", "Yo‘q"))

    def queryset(self, request, qs):
        v = self.value()
        if v == "yes":
            return qs.filter(budget_from__isnull=False) | qs.filter(budget_to__isnull=False)
        if v == "no":
            return qs.filter(budget_from__isnull=True, budget_to__isnull=True)
        return qs


# ---------------- Application Admin ----------------
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [ApplicationAttachmentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("tour", "country", "city", "assigned_to")

    list_display = (
        "full_name",
        "tour_link",
        "dates_people",
        "budget_badge",
        "preferred_contact",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = (
        "status", "preferred_contact", "assigned_to", "created_at",
        HasBudgetFilter, "tour",  "is_active",
    )
    search_fields = ("^full_name", "^phone", "^email", "alt_destination", "tour__title", "message")
    autocomplete_fields = ("tour", "country", "city", "assigned_to")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 50
    save_on_top = True
    date_hierarchy = "created_at"
    actions = [
        make_active, make_inactive, soft_delete, restore,
        mark_new, mark_in_review, mark_contacted, mark_won, mark_lost, mark_spam,
    ]

    @admin.display(description="Tur", ordering="tour__title")
    def tour_link(self, obj):
        if not obj.tour_id:
            return obj.alt_destination or "—"
        url = reverse("admin:tours_tour_change", args=(obj.tour_id,))
        return format_html('<a href="{}">{}</a>', url, obj.tour.title)

    @admin.display(description="Sana / Kun / Odam")
    def dates_people(self, obj):
        parts = []
        if obj.desired_start_date:
            parts.append(obj.desired_start_date.strftime("%Y-%m-%d"))
        if obj.days:
            parts.append(f"{obj.days} kun")
        total = (obj.adults or 0) + (obj.children or 0) + (obj.infants or 0)
        parts.append(f"{total} kishi")
        return " · ".join(parts)

    @admin.display(description="Byudjet", ordering="budget_from")
    def budget_badge(self, obj):
        if obj.budget_from is None and obj.budget_to is None:
            return "—"
        if obj.budget_from and obj.budget_to:
            return f"{obj.budget_from:.0f}–{obj.budget_to:.0f} {obj.currency}"
        if obj.budget_from:
            return f"≥ {obj.budget_from:.0f} {obj.currency}"
        return f"≤ {obj.budget_to:.0f} {obj.currency}"


# ---------------- ContactMessage Admin ----------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "email", "phone",
        "subject", "status", "assigned_to", "created_at",
    )
    list_filter = ("status", "subject", "assigned_to", "created_at", "is_active")
    search_fields = ("^full_name", "^email", "^phone", "message")
    autocomplete_fields = ("assigned_to",)
    readonly_fields = ("created_at", "updated_at", "client_ip", "user_agent", "referrer")
    ordering = ("-created_at",)
    list_per_page = 50
    date_hierarchy = "created_at"
    actions = [
        make_active, make_inactive, soft_delete, restore,
        cm_mark_new, cm_mark_read, cm_mark_answered, cm_mark_spam,
    ]
