from pathlib import Path
from datetime import timedelta
import os

# =========================
# Helpers (ENV parsing)
# =========================
def _as_bool(v, default=False):
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")

def _as_list(v, sep=","):
    if not v:
        return []
    return [x.strip() for x in str(v).split(sep) if x.strip()]

# =========================
# ✅ Base Directory
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ✅ Core
# =========================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-zfz0bi^i%p(0=!mzh$=p37f&&o-pg4w##61pzkn-#)4@5ocj&5')
DEBUG = _as_bool(os.environ.get('DEBUG', 'true'))

ALLOWED_HOSTS = _as_list(os.environ.get('ALLOWED_HOSTS')) or [
    '127.0.0.1', 'localhost', 'backend'
]

# Frontend base (used in CORS/CSRF)
FRONTEND_HOST = os.environ.get('FRONTEND_HOST', 'http://localhost:3000')
FRONTEND_ALT  = os.environ.get('FRONTEND_ALT',  'http://localhost:5173')

# =========================
# ✅ CSRF / CORS
# =========================
CSRF_TRUSTED_ORIGINS = _as_list(os.environ.get('CSRF_TRUSTED_ORIGINS')) or [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    FRONTEND_HOST,
    FRONTEND_ALT,
]
CORS_ALLOW_ALL_ORIGINS = _as_bool(os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'true'))  # dev only
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = _as_list(os.environ.get('CORS_ALLOWED_ORIGINS')) or [
    FRONTEND_HOST, FRONTEND_ALT
]

# =========================
# ✅ Installed Apps
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'django_filters',
    'corsheaders',
    'channels',
    'django_extensions',
    'drf_spectacular',               # ← NEW (أنت مستخدمه في REST_FRAMEWORK)

    # Local apps
    'core',
    'customers',
    'notifications',
    'accounts',
    'approvals',
    'shared',
    'suppliers',
    # 'inventory',
    'projects',
    'files',                         # التطبيق القديم
    'pre_tender',                    # ← NEW (التطبيق الجديد)
]

# =========================
# ✅ Middleware
# =========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================
# ✅ REST Framework
# =========================
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',   # dev only
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# =========================
# ✅ Simple JWT
# =========================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.CustomTokenSerializer',
}

# =========================
# ✅ Templates
# =========================
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

# =========================
# ✅ URL/ASGI/WSGI
# =========================
ROOT_URLCONF = 'erp_system.urls'
WSGI_APPLICATION = 'erp_system.wsgi.application'
ASGI_APPLICATION = 'erp_system.asgi.application'

# =========================
# ✅ Channels (Redis)
# =========================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": { "hosts": [("redis", 6379)] },
    },
}

# =========================
# ✅ Database
# =========================
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# =========================
# ✅ Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# ✅ Localization
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Dubai')
USE_I18N = True
USE_TZ = True

# =========================
# ✅ Static and Media
# =========================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# ✅ Custom User model
# =========================
AUTH_USER_MODEL = 'accounts.CustomUser'

# =========================
# ✅ Email (from ENV)
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = _as_bool(os.environ.get('EMAIL_USE_TLS', 'true'))
EMAIL_USE_SSL = _as_bool(os.environ.get('EMAIL_USE_SSL', 'false'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # لا تضع Default هنا
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    (f'{EMAIL_HOST_USER}' if EMAIL_HOST_USER else 'webmaster@localhost')
)

# =========================
# ✅ App URLs / Branding
# =========================
SITE_BASE_URL = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:8000')

# =========================
# ✅ Expiry reminders
# =========================
DEFAULT_REMINDER_WINDOWS = [int(x) for x in _as_list(os.environ.get('DEFAULT_REMINDER_WINDOWS'))] \
    if os.environ.get('DEFAULT_REMINDER_WINDOWS') else [14, 7, 3, 1, 0]

NOTIFY_FALLBACK_EMAILS = _as_list(os.environ.get('NOTIFY_FALLBACK_EMAILS'))
