from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-not-secure')
DEBUG = config('DEBUG', cast=bool, default=True)
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
ALLOWED_HOSTS = [
    "horuntravel.com",
    "www.horuntravel.com",
    "127.0.0.1",  # health-check yoki lokal test uchun
    "localhost",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Admin/CSRF uchun
CSRF_TRUSTED_ORIGINS = [
    "https://horuntravel.com",
    "https://www.horuntravel.com",

]

INSTALLED_APPS = [
    "jazzmin",
    # "unfold",
    "modeltranslation",
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    # 3rd-party
    'rest_framework', 'django_filters', 'drf_spectacular', 'corsheaders', "django_ckeditor_5",
    # local apps
    'common', 'tours', 'pages', 'siteinfo', 'locations', 'leads',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "core.middleware.APILanguageMiddleware",
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # hozircha sqlite; keyin Postgresga o‘tamiz
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LANGUAGE_CODE = 'uz'

LANGUAGES = [
    ("uz", "Oʻzbekcha"),
    ("ru", "Русский"),
    ("en", "English"),
]

# ModelTranslation sozlamalari
MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"
MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("uz", "en", "ru")  # topilmasa qaysi tilga qaytish

TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = "/var/www/horuntravel/static"
MEDIA_ROOT  = "/var/www/horuntravel/media"

CORS_ALLOW_ALL_ORIGINS = True  # prod’da domen bilan cheklaysiz

# REST_FRAMEWORK = {
#     'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
#     'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 12,
# }


SPECTACULAR_SETTINGS = {
    "TITLE": "Horun Travel API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # /api/schema/ dan tashqari UI’lar schema’ni ichidan olmaydi

    # Swagger/Redoc sahifalarini hammaga ochish:
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],

    # (ixtiyoriy) Bearer auth tugmasi
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
}


JAZZMIN_SETTINGS = {
    "site_title": "Horun Travel Admin",
    "site_header": "Horun Travel",
    "site_brand": "Horun Admin",
    "welcome_sign": "Assalomu alaykum",
    "show_sidebar": True,
    "hide_apps": [],
    "hide_models": [],
    # Menyuni guruhlash misoli:
    "order_with_respect_to": ["locations", "tours", "leads", "siteinfo"],
}
# UNFOLD = {
#     "SITE_HEADER": "Horun Travel",
#     "SHOW_HISTORY": True,
# }

CKEDITOR_5_UPLOADS_DIRECTORY = "uploads/ckeditor5/"
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "bold", "italic", "underline", "|",
            "bulletedList", "numberedList", "outdent", "indent", "|",
            "link", "blockQuote", "insertTable", "|",
            "undo", "redo", "removeFormat", "|",
            "mediaEmbed", "codeBlock", "horizontalLine", "specialCharacters",
        ],
        "language": "uz",
    },
    # Matn uzunroq joylarda biroz keng toolbar
    "long": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "strikethrough",
            "bulletedList", "numberedList", "todoList", "outdent", "indent", "|",
            "link", "blockQuote", "insertTable", "mediaEmbed", "|",
            "undo", "redo", "code", "codeBlock", "horizontalLine", "removeFormat", "|",
            "specialCharacters", "subscript", "superscript"
        ],
        "language": "uz",
    },
}
# CKEDITOR_5_USER_GROUPS = {
#     "default": {
#         "allow_all": True,
#         "groups": ["Editors", "Admins"],  # faqat shu guruhlar yuklay oladi
#     }
# }

# DRF
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        # Keyinchalik JWT qo‘shish mumkin
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # prod’da kerakli joylarda o‘zgartirasiz
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",  # ariza/contact POST uchun qo‘shimcha throttle ko‘rsatamiz
        "user": "120/min",
        "applications": "10/min",
        "contacts": "20/min",
    },
}

# Email jo'natish uchun
DEFAULT_FROM_EMAIL = "noreply@horuntravel.com"

# Adminlarga boradigan qabul qiluvchilar (bir nechta bo‘lishi mumkin)
NOTIFY_EMAILS = ["info@horuntravel.com"]

# Devda test qilish uchun (konsolga chiqaradi), prod’da SMTP qo‘ying
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# PROD misol:
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.yandex.com"
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# EMAIL_HOST_USER = "info@horuntravel.com"
# EMAIL_HOST_PASSWORD = "parol"

# (Ixtiyoriy) Telegram sozlamalari — bo‘lsa yuboradi, bo‘lmasa skip
TELEGRAM_BOT_TOKEN = "8317871106:AAFR5vEo4AP3nT4ZDtQvj8-myNvXRYqZs6M"  # "123456:ABC..."
TELEGRAM_ADMIN_CHAT_ID = "758934089"  # "-100123456789" yoki "123456789"

# # reverse-proxy orqasida https-ni to‘g‘ri tanish uchun
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
#
# # admin & CSRF
# CSRF_TRUSTED_ORIGINS = ["https://horuntravel.com", "https://www.horuntravel.com"]
