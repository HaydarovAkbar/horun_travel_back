# core/middleware.py
from django.utils import translation
from django.conf import settings

# header nomlarini belgilaymiz
PREFERRED_HEADER = "HTTP_X_LANGUAGE"        # 'X-Language: uz'
FALLBACK_HEADER  = "HTTP_ACCEPT_LANGUAGE"   # 'Accept-Language: uz,ru;q=0.8,...'

def _normalize(lang: str) -> str | None:
    """'uz-UZ', 'ru_RU', 'en-us' -> 'uz'/'ru'/'en' kabi qisqartma.
       settings.LANGUAGES dagi kodlarga mos kelganini qaytaradi."""
    if not lang:
        return None
    lang = lang.replace("_", "-").lower().strip()
    # "uz-uz,ru;q=0.8" kabi bo‘lsa — vergulgacha
    lang = lang.split(",")[0].strip()
    # faqat primary subtagni olaylik: 'uz-latn-uz' -> 'uz'
    primary = lang.split("-")[0]
    supported = {code for code, _ in getattr(settings, "LANGUAGES", [])}
    if primary in supported:
        return primary
    # to‘g‘ridan ham tekshirib ko‘ramiz (masalan 'en-us' to‘liq)
    if lang in supported:
        return lang
    return None

class APILanguageMiddleware:
    """
    Header orqali API tilini boshqarish:
      - 1-prioritet: X-Language: uz|ru|en
      - 2-prioritet: Accept-Language
    Topilmasa -> LANGUAGE_CODE (uz) ga tushadi.
    Response'da Content-Language qo'shib beradi.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1) X-Language
        lang = _normalize(request.META.get(PREFERRED_HEADER, ""))

        # 2) Accept-Language (agar 1 topilmasa)
        if not lang:
            lang = _normalize(request.META.get(FALLBACK_HEADER, ""))

        # 3) Default
        if not lang:
            lang = settings.LANGUAGE_CODE.split("-")[0]

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        try:
            response = self.get_response(request)
        finally:
            translation.deactivate()

        # Javobga ham tilni qo'shib qo'yamiz (foydali)
        if hasattr(response, "headers"):
            response.headers["Content-Language"] = lang
        else:
            response["Content-Language"] = lang

        return response
