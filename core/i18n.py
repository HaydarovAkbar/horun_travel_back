# core/i18n.py
from django.utils.translation import get_language

def lang():  # "uz" / "ru" / "en"
    return (get_language() or "uz").split("-")[0]

def pick_lang(obj, base_name: str):
    """
    modeltranslation maydoni: base_name -> base_name_{lang}
    obj.title -> obj.title_uz/ru/en dan aktiv tilga mos qiymatni oladi.
    """
    l = lang()
    attr = f"{base_name}_{l}"
    return getattr(obj, attr, getattr(obj, base_name, ""))
