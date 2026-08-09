"""
Development settings for LandMarket project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database URL override for development
DATABASE_URL = config('DATABASE_URL', default='postgresql://landmarket_user:landmarket_password@localhost:5432/landmarket')

# Parse database URL
import dj_database_url
DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery Configuration for development
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True

# Logging for development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['landmarket']['level'] = 'DEBUG'

# Media files in development (local storage)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Cache configuration (use dummy cache for development if needed)
# CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

print("🚀 LandMarket running in DEVELOPMENT mode")
print(f"📍 Database: {DATABASES['default']['HOST']}:{DATABASES['default']['PORT']}")
print(f"🔍 Elasticsearch: {ELASTICSEARCH_DSL['default']['hosts']}")
print(f"🗄️  Redis: {REDIS_URL}")
print(f"🔑 Google Maps API: {'✅ Configured' if GOOGLE_MAPS_API_KEY else '❌ Missing'}")