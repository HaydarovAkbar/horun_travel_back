from modeltranslation.translator import register, TranslationOptions
from .models import TourCategory, TourTag, Tour, ItineraryDay, TourImage, TourVideo

@register(TourCategory)
class TourCategoryTR(TranslationOptions):
    fields = ("name",)

# @register(TourTag)
# class TourTagTR(TranslationOptions):
#     fields = ("name",)

@register(Tour)
class TourTR(TranslationOptions):
    fields = ("title", "short_description", "long_description", "meta_title", "meta_description")

@register(ItineraryDay)
class ItineraryDayTR(TranslationOptions):
    fields = ("title", "description")

@register(TourImage)
class TourImageTR(TranslationOptions):
    fields = ("alt",)

@register(TourVideo)
class TourVideoTR(TranslationOptions):
    fields = ("title",)
