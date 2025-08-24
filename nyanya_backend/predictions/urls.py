"""
Prediction API URLs

Only essential endpoints for Streamlit Dashboard
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard essentials only
    path('current-week/', views.current_week_prediction, name='current-week-prediction'),
    path('dashboard-cards/', views.dashboard_cards, name='dashboard-cards'),
    path('chart-data/', views.chart_data, name='chart-data'),
    path('simulate/', views.simulate_weeks, name='simulate-weeks'),
    path('status-cards/', views.status_cards, name='status-cards'),
    # New chart APIs
    path('market-insights/', views.market_insights_chart, name='market-insights'),
    path('business-insights/', views.business_insights_data, name='business-insights'),
    # Tips API
    path('agricultural-tips/', views.agricultural_tips, name='agricultural-tips'),
]
