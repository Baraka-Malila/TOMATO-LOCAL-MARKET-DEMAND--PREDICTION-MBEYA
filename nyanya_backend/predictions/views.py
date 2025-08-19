"""
Dashboard Prediction Views for Tomato Market Mbeya
"""

from datetime import datetime, timedelta
from django.db.models import Count, Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Prediction
from .model_loader import predictor
from market_data.models import MarketData


@api_view(['GET'])
def current_week_prediction(request):
    """Current week's tomato demand prediction"""
    
    now = datetime.now()
    current_week = now.isocalendar()[1]
    
    try:
        prediction, confidence = predictor.predict(
            rainfall_mm=75.0,
            temperature_c=23.0,
            market_day=True,
            school_open=True,
            disease_alert='Absence',
            last_week_demand='Medium',
            week=current_week,
            month=now.strftime('%B')
        )
        
        colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        
        return Response({
            'week': current_week,
            'predicted_demand': prediction,
            'confidence': round(confidence, 2),
            'status_color': colors[prediction],
            'confidence_percentage': f"{int(confidence * 100)}%"
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def dashboard_cards(request):
    """Data for the 4 dashboard metric cards"""
    
    # Real data calculations
    total_predictions = Prediction.objects.count()
    
    week_start = datetime.now() - timedelta(days=7)
    weekly_predictions = Prediction.objects.filter(timestamp__gte=week_start).count()
    
    # Calculate real weekly change
    prev_week_start = datetime.now() - timedelta(days=14)
    prev_week_end = datetime.now() - timedelta(days=7)
    prev_weekly = Prediction.objects.filter(
        timestamp__gte=prev_week_start, 
        timestamp__lt=prev_week_end
    ).count()
    
    weekly_change = "+0%" if prev_weekly == 0 else f"{((weekly_predictions - prev_weekly) / prev_weekly * 100):+.0f}%"
    
    avg_confidence = Prediction.objects.aggregate(avg=Avg('confidence_score'))['avg'] or 0
    performance_percent = int(avg_confidence * 100)
    
    high_demand_count = Prediction.objects.filter(predicted_demand='High').count()
    
    # Calculate real total change (last 30 days vs previous 30)
    month_ago = datetime.now() - timedelta(days=30)
    two_months_ago = datetime.now() - timedelta(days=60)
    
    last_month = Prediction.objects.filter(timestamp__gte=month_ago).count()
    prev_month = Prediction.objects.filter(
        timestamp__gte=two_months_ago, 
        timestamp__lt=month_ago
    ).count()
    
    total_change = "+0%" if prev_month == 0 else f"{((last_month - prev_month) / prev_month * 100):+.0f}%"
    
    return Response({
        'total_predictions': {
            'value': f"{total_predictions:,}",
            'change': total_change,
            'trend': 'up' if '+' in total_change else 'down',
            'label': 'TOTAL PREDICTIONS'
        },
        'weekly_predictions': {
            'value': f"{weekly_predictions:,}",
            'change': weekly_change,
            'trend': 'up' if '+' in weekly_change else 'down',
            'label': 'THIS WEEK'
        },
        'model_performance': {
            'value': f"{performance_percent}%",
            'change': '+2.6%',  # Keep this mock as we don't track historical performance
            'trend': 'up',
            'label': 'ACCURACY'
        },
        'high_demand_weeks': {
            'value': f"{high_demand_count:,}",
            'change': '+5.8%',  # Keep this mock for now
            'trend': 'up',
            'label': 'HIGH DEMAND'
        }
    })


@api_view(['GET'])
def chart_data(request):
    """Historical data for dashboard charts"""
    
    recent_data = MarketData.objects.order_by('-year', '-week')[:12]
    
    chart_points = []
    demand_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    
    for data in reversed(recent_data):
        chart_points.append({
            'week': f"W{data.week}",
            'demand_level': data.market_demand,
            'demand_value': {'High': 3, 'Medium': 2, 'Low': 1}[data.market_demand],
            'rainfall': data.rainfall_mm,
            'temperature': data.temperature_c
        })
        demand_counts[data.market_demand] += 1
    
    return Response({
        'trend_data': chart_points,
        'demand_distribution': demand_counts,
        'total_weeks': len(chart_points)
    })


@api_view(['GET'])
def simulate_weeks(request):
    """Interactive simulation data for week-by-week playback"""
    
    start_week = int(request.GET.get('start', 1))
    end_week = int(request.GET.get('end', 20))
    year = int(request.GET.get('year', 2025))
    
    market_data = MarketData.objects.filter(
        year=year,
        week__gte=start_week,
        week__lte=end_week
    ).order_by('week')
    
    simulation_frames = []
    
    for week_data in market_data:
        try:
            prediction, confidence = predictor.predict(
                rainfall_mm=week_data.rainfall_mm,
                temperature_c=week_data.temperature_c,
                market_day=week_data.market_day,
                school_open=week_data.school_open,
                disease_alert=week_data.disease_alert,
                last_week_demand=week_data.last_week_demand,
                week=week_data.week,
                month=week_data.month
            )
            
            simulation_frames.append({
                'week': week_data.week,
                'month': week_data.month,
                'predicted_demand': prediction,
                'actual_demand': week_data.market_demand,
                'confidence': round(confidence, 2),
                'match': prediction == week_data.market_demand
            })
            
        except Exception:
            continue
    
    return Response({
        'frames': simulation_frames,
        'total_frames': len(simulation_frames),
        'play_speed': 500
    })
