"""
Production settings for LandMarket project.
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='landmarket.com,www.landmarket.com', cast=lambda v: [s.strip() for s in v.split(',')])

# Database configuration
DATABASE_URL = config('DATABASE_URL')
DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
DATABASES['default']['CONN_MAX_AGE'] = 600

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])
CORS_ALLOW_CREDENTIALS = True

# Static and media files (AWS S3)
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    
    # Static files settings
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_SECURE_URLS = True
    AWS_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    
    # Media files settings
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Fallback to local storage with WhiteNoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Sentry error tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=False,
            ),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment='production',
    )

# Logging configuration
LOGGING['handlers']['file']['filename'] = '/var/log/landmarket/django.log'
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['root']['level'] = 'WARNING'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Celery configuration for production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Cache configuration
CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS'] = {"max_connections": 50}

# Performance optimizations
CONN_MAX_AGE = 600  # 10 minutes

# Health checks
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,     # in MB
}

print("🚀 LandMarket running in PRODUCTION mode")
print(f"📍 Database: {DATABASES['default']['HOST']}")
print(f"🔒 SSL Redirect: {SECURE_SSL_REDIRECT}")
print(f"☁️  S3 Storage: {'✅ Enabled' if AWS_ACCESS_KEY_ID else '❌ Local'}")
print(f"📊 Sentry: {'✅ Enabled' if SENTRY_DSN else '❌ Disabled'}")