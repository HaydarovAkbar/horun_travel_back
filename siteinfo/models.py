# siteinfo/models.py
from django.db import models
from django.core.validators import RegexValidator, URLValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel
from locations.models import Country, City


class SiteSettings(BaseModel):
    """
    Umumiy sayt sozlamalari (bir dona yozuv yetarli bo‘ladi — singleton).
    """
    singleton_key = models.CharField(
        _("Yagona kalit"),
        max_length=32,
        unique=True,
        default="default",
        help_text=_("Ushbu yozuvni unikallash uchun xizmat qiladi (odatda 'default')."),
    )

    org_name = models.CharField(
        _("Tashkilot nomi"),
        max_length=200,
        blank=True,
        help_text=_("Masalan: Horun Travel"),
    )
    slogan = models.CharField(
        _("Slogan"),
        max_length=200,
        blank=True,
        help_text=_("Qisqa shior (ixtiyoriy)."),
    )

    logo = models.ImageField(
        _("Logo (yorug‘ mavzu)"),
        upload_to="site/logo/",
        blank=True,
    )
    logo_dark = models.ImageField(
        _("Logo (qorong‘i mavzu)"),
        upload_to="site/logo/",
        blank=True,
    )
    favicon = models.ImageField(
        _("Favicon"),
        upload_to="site/favicon/",
        blank=True,
    )

    primary_phone = models.CharField(
        _("Asosiy telefon"),
        max_length=32,
        blank=True,
        help_text=_("Masalan: +998 90 123 45 67"),
    )
    primary_email = models.EmailField(
        _("Asosiy email"),
        blank=True,
        help_text=_("Masalan: info@namuna.uz"),
    )

    meta_title = models.CharField(
        _("Meta sarlavha"),
        max_length=255,
        blank=True,
        help_text=_("SEO uchun sarlavha (asosiy sahifa)."),
    )
    meta_description = models.CharField(
        _("Meta tavsif"),
        max_length=255,
        blank=True,
        help_text=_("SEO uchun qisqa tavsif (asosiy sahifa)."),
    )

    class Meta:
        verbose_name = _("Sayt sozlamalari")
        verbose_name_plural = _("Sayt sozlamalari")

    def __str__(self):
        return f"{self.org_name or 'Sayt sozlamalari'}"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(singleton_key="default", defaults={"is_active": True})
        return obj


class ContactChannel(BaseModel):
    """
    Aloqa kanali (telefon, email, Telegram, WhatsApp va hokazo).
    Bir nechta yozuv bo‘lishi mumkin, tartib (order) bo‘yicha chiqariladi.
    """
    TYPE_CHOICES = (
        ("phone", _("Telefon")),
        ("email", _("Email")),
        ("whatsapp", _("WhatsApp")),
        ("telegram", _("Telegram")),
        ("website", _("Veb-sayt")),
        ("fax", _("Faks")),
        ("other", _("Boshqa")),
    )

    settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="contacts",
        verbose_name=_("Sayt sozlamalari")
    )
    type = models.CharField(
        _("Kanal turi"), max_length=16, choices=TYPE_CHOICES, default="phone"
    )
    label = models.CharField(
        _("Yorliq"), max_length=64, blank=True,
        help_text=_("Masalan: Call center, Sotuv, Booking va h.k.")
    )
    value = models.CharField(
        _("Qiymat"), max_length=256,
        help_text=_("Telefon: +998..., Email: example@..., Telegram: https://t.me/... va h.k.")
    )
    order = models.PositiveIntegerField(
        _("Tartib"), default=0, db_index=True
    )
    is_primary = models.BooleanField(
        _("Asosiy kanal"), default=False
    )

    class Meta:
        verbose_name = _("Aloqa kanali")
        verbose_name_plural = _("Aloqa kanallari")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_type_display()} — {self.value}"

    def clean(self):
        if self.type == "email":
            EmailValidator()(self.value)
        elif self.type in ("website", "telegram"):
            URLValidator()(self.value)
        elif self.type in ("phone", "whatsapp", "fax"):
            phone_re = RegexValidator(
                regex=r"^\+?[0-9\-\s\(\)]{6,}$",
                message=_("Telefon formati noto‘g‘ri."),
            )
            phone_re(self.value)


class SocialLink(BaseModel):
    """
    Ijtimoiy tarmoq havolalari.
    """
    PROVIDERS = (
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
        ("telegram", "Telegram"),
        ("twitter", "X / Twitter"),
        ("linkedin", "LinkedIn"),
        ("vk", "VK"),
        ("other", _("Boshqa")),
    )

    settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="socials",
        verbose_name=_("Sayt sozlamalari")
    )
    provider = models.CharField(
        _("Platforma"), max_length=20, choices=PROVIDERS, default="instagram"
    )
    label = models.CharField(
        _("Yorliq"), max_length=64, blank=True,
        help_text=_("Masalan: @username yoki qisqa izoh (ixtiyoriy).")
    )
    url = models.URLField(
        _("Havola"), max_length=500
    )
    order = models.PositiveIntegerField(
        _("Tartib"), default=0, db_index=True
    )

    class Meta:
        verbose_name = _("Ijtimoiy tarmoq")
        verbose_name_plural = _("Ijtimoiy tarmoqlar")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_provider_display()} — {self.url}"


class Location(BaseModel):
    """
    Ofis/yoki filial manzili. Bir nechta bo‘lishi mumkin.
    """
    settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="locations",
        verbose_name=_("Sayt sozlamalari")
    )
    name = models.CharField(
        _("Joy nomi"), max_length=120, blank=True,
        help_text=_("Masalan: Bosh ofis, Samarqand filiali va h.k.")
    )
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="org_locations",
        verbose_name=_("Davlat")
    )
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, related_name="org_locations",
        null=True, blank=True, verbose_name=_("Shahar")
    )
    address_line = models.CharField(
        _("Manzil"), max_length=255, blank=True
    )
    postal_code = models.CharField(
        _("Pochta indeksi"), max_length=20, blank=True
    )

    lat = models.DecimalField(
        _("Kenglik (lat)"), max_digits=9, decimal_places=6, null=True, blank=True
    )
    lng = models.DecimalField(
        _("Uzunlik (lng)"), max_digits=9, decimal_places=6, null=True, blank=True
    )
    map_embed_url = models.URLField(
        _("Xarita (embed URL)"), max_length=800, blank=True,
        help_text=_("Google Maps embed havolasi (ixtiyoriy).")
    )
    place_id = models.CharField(
        _("Place ID"), max_length=128, blank=True
    )

    order = models.PositiveIntegerField(
        _("Tartib"), default=0, db_index=True
    )
    is_primary = models.BooleanField(
        _("Asosiy manzil"), default=False
    )

    class Meta:
        verbose_name = _("Manzil")
        verbose_name_plural = _("Manzillar")
        ordering = ["order", "id"]

    def __str__(self):
        line = self.name or (self.city.name if self.city else self.country.name)
        return f"{line}"


class WorkingHour(BaseModel):
    """
    Ish vaqti (har bir manzil uchun haftalik jadval).
    """
    WEEKDAYS = (
        (0, _("Dushanba")),
        (1, _("Seshanba")),
        (2, _("Chorshanba")),
        (3, _("Payshanba")),
        (4, _("Juma")),
        (5, _("Shanba")),
        (6, _("Yakshanba")),
    )

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="hours",
        verbose_name=_("Manzil")
    )
    weekday = models.PositiveSmallIntegerField(
        _("Hafta kuni"), choices=WEEKDAYS
    )
    closed = models.BooleanField(
        _("Yopiq"), default=False, help_text=_("Ushbu kunda ishlanmaydi.")
    )
    open_time = models.TimeField(
        _("Ochiladi"), null=True, blank=True
    )
    close_time = models.TimeField(
        _("Yopiladi"), null=True, blank=True
    )
    order = models.PositiveIntegerField(
        _("Tartib"), default=0
    )

    class Meta:
        verbose_name = _("Ish vaqti")
        verbose_name_plural = _("Ish vaqtlari")
        unique_together = (("location", "weekday"),)
        ordering = ["order", "weekday", "id"]

    def __str__(self):
        return f"{self.location} — {self.get_weekday_display()}"

    def clean(self):
        if not self.closed:
            if not self.open_time or not self.close_time:
                raise ValidationError(_("Ochiq bo‘lsa, ochilish/yopilish vaqtlarini kiriting."))
            if self.open_time >= self.close_time:
                raise ValidationError(_("Ochilish vaqti yopilish vaqtidan kichik bo‘lishi kerak."))


class AboutPage(BaseModel):
    """
    'Biz haqimizda' sahifasi uchun bosh ma’lumot.
    """
    singleton_key = models.CharField(
        _("Yagona kalit"),
        max_length=32,
        unique=True,
        default="about",
    )

    hero_title = models.CharField(
        _("Sarlavha"), max_length=200, blank=True
    )
    hero_subtitle = models.CharField(
        _("Qisqa tavsif"), max_length=300, blank=True
    )
    hero_image = models.ImageField(
        _("Fon rasm"), upload_to="pages/about/", blank=True
    )
    video_url = models.URLField(
        _("Video havola"), max_length=500, blank=True
    )

    meta_title = models.CharField(
        _("Meta sarlavha"), max_length=255, blank=True
    )
    meta_description = models.CharField(
        _("Meta tavsif"), max_length=255, blank=True
    )

    class Meta:
        verbose_name = _("Biz haqimizda (sahifa)")
        verbose_name_plural = _("Biz haqimizda (sahifa)")

    def __str__(self):
        return _("Biz haqimizda sahifasi")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(singleton_key="about", defaults={"is_active": True})
        return obj


class AboutSection(BaseModel):
    """
    'Biz haqimizda' sahifasidagi bo‘lim (blok): sarlavha + matn + rasm.
    """
    about = models.ForeignKey(
        AboutPage, on_delete=models.CASCADE, related_name="sections",
        verbose_name=_("Sahifa")
    )
    title = models.CharField(
        _("Bo‘lim sarlavhasi"), max_length=200, blank=True
    )
    body = models.TextField(
        _("Bo‘lim matni"), blank=True,
        help_text=_("HTML yoki Markdown matn (ixtiyoriy).")
    )
    image = models.ImageField(
        _("Rasm"), upload_to="pages/about/sections/", blank=True
    )
    order = models.PositiveIntegerField(
        _("Tartib"), default=0, db_index=True
    )

    class Meta:
        verbose_name = _("Bo‘lim")
        verbose_name_plural = _("Bo‘limlar")
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"{_('Bo‘lim')} #{self.pk}"


class ContactPage(BaseModel):
    """
    'Aloqa' sahifasi uchun bosh ma’lumot (intro/hero).
    Qolgan aloqa ma’lumotlari SiteSettings/ContactChannel/Location’dan keladi.
    """
    singleton_key = models.CharField(
        _("Yagona kalit"),
        max_length=32,
        unique=True,
        default="contact",
    )

    hero_title = models.CharField(
        _("Sarlavha"), max_length=200, blank=True
    )
    hero_subtitle = models.CharField(
        _("Qisqa tavsif"), max_length=300, blank=True
    )
    intro_html = models.TextField(
        _("Kirish matni (HTML)"), blank=True
    )

    meta_title = models.CharField(
        _("Meta sarlavha"), max_length=255, blank=True
    )
    meta_description = models.CharField(
        _("Meta tavsif"), max_length=255, blank=True
    )

    class Meta:
        verbose_name = _("Aloqa (sahifa)")
        verbose_name_plural = _("Aloqa (sahifa)")

    def __str__(self):
        return _("Aloqa sahifasi")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(singleton_key="contact", defaults={"is_active": True})
        return obj
