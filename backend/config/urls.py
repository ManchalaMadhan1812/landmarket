"""
URL configuration for LandMarket project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API URL patterns
api_patterns = [
    path('auth/', include('apps.authentication.urls')),
    path('properties/', include('apps.properties.urls')),
    path('messaging/', include('apps.messaging.urls')),
    path('search/', include('apps.search.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('core/', include('apps.core.urls')),
    path('subscriptions/', include('apps.payments.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include(api_patterns)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('health/', include('health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin site customization
admin.site.site_header = "LandMarket Administration"
admin.site.site_title = "LandMarket Admin"
admin.site.index_title = "Welcome to LandMarket Administration"