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
]
