"""
Market Data Views for Dashboard
"""

from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MarketData


@api_view(['GET'])
def market_history(request):
    """Get historical market data for dashboard background info"""
    
    total_weeks = MarketData.objects.count()
    demand_breakdown = MarketData.objects.values('market_demand').annotate(
        count=Count('id')
    )
    
    recent_weeks = MarketData.objects.order_by('-year', '-week')[:10]
    recent_data = [
        {
            'week': item.week,
            'year': item.year,
            'actual_demand': item.market_demand,
            'month': item.month
        }
        for item in recent_weeks
    ]
    
    return Response({
        'total_weeks_available': total_weeks,
        'demand_breakdown': {item['market_demand']: item['count'] for item in demand_breakdown},
        'recent_weeks': recent_data
    })
