from modeltranslation.translator import register, TranslationOptions
from .models import SiteSettings, ContactChannel, SocialLink, Location, AboutPage, AboutSection, ContactPage

@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = ("org_name", "slogan", "meta_title", "meta_description")

@register(ContactChannel)
class ContactChannelTR(TranslationOptions):
    fields = ("label",)

@register(SocialLink)
class SocialLinkTR(TranslationOptions):
    fields = ("label",)

@register(Location)
class LocationTR(TranslationOptions):
    fields = ("name", "address_line")

@register(AboutPage)
class AboutPageTR(TranslationOptions):
    fields = ("hero_title", "hero_subtitle", "meta_title", "meta_description")

@register(AboutSection)
class AboutSectionTR(TranslationOptions):
    fields = ("title", "body")

@register(ContactPage)
class ContactPageTR(TranslationOptions):
    fields = ("hero_title", "hero_subtitle", "intro_html", "meta_title", "meta_description")
