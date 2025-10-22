from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, EmailValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from common.models import BaseModel
from locations.models import Country, City
from tours.models import Tour

User = get_user_model()


class Application(BaseModel):
    """
    Tur tanlab ariza qoldirish (lead).
    Admin’da status orqali boshqariladi.
    """
    STATUS = (
        ("new", _("Yangi")),
        ("in_review", _("Ko‘rib chiqilmoqda")),
        ("contacted", _("Aloqa qilindi")),
        ("won", _("Sotildi / band qilindi")),
        ("lost", _("Yo‘qotildi")),
        ("spam", _("Spam / nojo‘ya")),
    )
    PREFERRED_CONTACT = (
        ("phone", _("Telefon")),
        ("whatsapp", "WhatsApp"),
        ("telegram", "Telegram"),
        ("email", _("Email")),
    )

    # Mijoz ma’lumoti
    full_name = models.CharField(
        _("To‘liq ism"), max_length=120,
        help_text=_("Masalan: Ali Valiyev"),
    )
    phone = models.CharField(
        _("Telefon"), max_length=32,
        help_text=_("Masalan: +998 90 123 45 67"),
        validators=[RegexValidator(r"^\+?[0-9\-\s\(\)]{6,}$")]
    )
    email = models.EmailField(_("Email"), blank=True, validators=[EmailValidator()])
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Mamlakat (mijoz)"),
        help_text=_("Mijoz istiqomat qiladigan mamlakat (ixtiyoriy)."),
        related_name="applicants_country"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Shahar (mijoz)"),
        help_text=_("Ixtiyoriy."),
        related_name="applicants_city"
    )
    preferred_contact = models.CharField(
        _("Aloqa usuli"), max_length=16, choices=PREFERRED_CONTACT, default="phone"
    )

    # Tur ma’lumoti
    tour = models.ForeignKey(
        Tour, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Tanlangan tur"),
        help_text=_("Agar mijoz aniq tur tanlagan bo‘lsa."),
        related_name="applications"
    )
    alt_destination = models.CharField(
        _("Muqobil yo‘nalish"), max_length=150, blank=True,
        help_text=_("Masalan: Turkiya, BAA... (tur tanlanmagan bo‘lsa).")
    )
    desired_start_date = models.DateField(
        _("Boshlanish sanasi"), null=True, blank=True
    )
    days = models.PositiveSmallIntegerField(
        _("Necha kun"), null=True, blank=True, validators=[MinValueValidator(1)]
    )
    adults = models.PositiveSmallIntegerField(
        _("Kattalar soni"), default=1, validators=[MinValueValidator(1)]
    )
    children = models.PositiveSmallIntegerField(
        _("Bolalar soni"), default=0
    )
    infants = models.PositiveSmallIntegerField(
        _("Chaqaloqlar soni"), default=0
    )

    # Byudjet (ixtiyoriy)
    currency = models.CharField(_("Valyuta"), max_length=3, default="USD")
    budget_from = models.DecimalField(
        _("Byudjet dan"), max_digits=12, decimal_places=2, null=True, blank=True
    )
    budget_to = models.DecimalField(
        _("Byudjet gacha"), max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Izoh va manba
    message = models.TextField(_("Izoh / talablar"), blank=True)
    status = models.CharField(_("Holat"), max_length=16, choices=STATUS, default="new")
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Mas’ul xodim"), related_name="assigned_applications"
    )

    # Trafik manbasi / kampaniya
    utm_source = models.CharField(_("UTM Source"), max_length=64, blank=True)
    utm_medium = models.CharField(_("UTM Medium"), max_length=64, blank=True)
    utm_campaign = models.CharField(_("UTM Campaign"), max_length=64, blank=True)
    referrer = models.CharField(_("Referrer URL"), max_length=500, blank=True)
    client_ip = models.GenericIPAddressField(_("Mijoz IP"), null=True, blank=True)
    user_agent = models.CharField(_("User-Agent"), max_length=300, blank=True)

    class Meta:
        verbose_name = _("Tur arizasi")
        verbose_name_plural = _("Tur arizalari")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.tour.title if self.tour_id else (self.alt_destination or 'Tur (aniqlanmagan)')}"

    def clean(self):
        # byudjet mantiqi
        if self.budget_from and self.budget_to and self.budget_from > self.budget_to:
            from django.core.exceptions import ValidationError
            raise ValidationError({"budget_to": _("'Byudjet gacha' qiymati 'Byudjet dan' dan katta bo‘lishi kerak.")})


class ApplicationAttachment(BaseModel):
    """
    Arizaga fayl biriktirish (ixtiyoriy).
    Masalan: pasport nusxasi, skrinshot, brif.
    """
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="attachments",
        verbose_name=_("Ariza")
    )
    file = models.FileField(_("Fayl"), upload_to="leads/attachments/")
    title = models.CharField(_("Nomi"), max_length=150, blank=True)

    class Meta:
        verbose_name = _("Biriktirilgan fayl")
        verbose_name_plural = _("Biriktirilgan fayllar")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.file.name


class ContactMessage(BaseModel):
    """
    Kontakt sahifasidan yuboriladigan umumiy xabar.
    """
    SUBJECT_CHOICES = (
        ("general", _("Umumiy savol")),
        ("booking", _("Bron / Band qilish")),
        ("support", _("Qo‘llab-quvvatlash")),
        ("partnership", _("Hamkorlik")),
        ("other", _("Boshqa")),
    )

    full_name = models.CharField(_("To‘liq ism"), max_length=120)
    email = models.EmailField(_("Email"), validators=[EmailValidator()])
    phone = models.CharField(
        _("Telefon"), max_length=32, blank=True,
        validators=[RegexValidator(r"^\+?[0-9\-\s\(\)]{6,}$")]
    )
    subject = models.CharField(_("Mavzu"), max_length=20, choices=SUBJECT_CHOICES, default="general")
    message = models.TextField(_("Xabar"))

    status = models.CharField(
        _("Holat"), max_length=16,
        choices=(("new", _("Yangi")), ("read", _("O‘qildi")), ("answered", _("Javob berildi")), ("spam", _("Spam"))),
        default="new"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Mas’ul xodim"), related_name="assigned_messages"
    )

    # texnik ma’lumotlar
    client_ip = models.GenericIPAddressField(_("Mijoz IP"), null=True, blank=True)
    user_agent = models.CharField(_("User-Agent"), max_length=300, blank=True)
    referrer = models.CharField(_("Referrer URL"), max_length=500, blank=True)

    class Meta:
        verbose_name = _("Kontakt xabar")
        verbose_name_plural = _("Kontakt xabarlar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.get_subject_display()}"
