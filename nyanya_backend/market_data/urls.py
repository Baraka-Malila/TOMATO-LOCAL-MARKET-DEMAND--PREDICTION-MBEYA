"""
Market Data URLs

Only what's needed for dashboard
"""

from django.urls import path
from . import views

urlpatterns = [
    # Only essential endpoint for historical data
    path('history/', views.market_history, name='market-history'),
]
