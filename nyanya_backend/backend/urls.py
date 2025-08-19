"""
URL Configuration for Agricultural Market Backend

Simple API for market data management and predictions.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="TOMATO LOCAL MARKET MBEYA",
        default_version='v1',
        description="""
        Tomato Market Demand Prediction API for Mbeya, Tanzania
        
        Features:
        - Weekly demand predictions (High/Medium/Low)
        - Market data analytics and trends
        - Interactive simulation data
        - Dashboard metrics and KPIs
        """,
        contact=openapi.Contact(email="contact@tomatomarket.mbeya"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # API endpoints (simplified)
    path('api/data/', include('market_data.urls')),
    path('api/predictions/', include('predictions.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
