"""
Dashboard Prediction Views for Tomato Market Mbeya
"""

from datetime import datetime, timedelta
from django.db.models import Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Prediction
from .model_loader import predictor
from market_data.models import MarketData


@api_view(['GET'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
    
    # Use actual model accuracy (95% based on training/testing)
    # avg_confidence represents prediction confidence, not model accuracy
    model_accuracy = 95  # Your actual model accuracy from training/validation
    
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
            'value': f"{model_accuracy}%",
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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


@api_view(['GET'])
@permission_classes([AllowAny])
def status_cards(request):
    """Real data for health and weather status cards"""
    
    latest_data = MarketData.objects.order_by('-year', '-week').first()
    
    if not latest_data:
        return Response({
            'weather': {'status': 'No data', 'details': 'Weather data unavailable'},
            'health': {'status': 'No data', 'details': 'Health data unavailable'}
        })
    
    # Weather status based on real data
    temp = float(latest_data.temperature_c)
    rainfall = float(latest_data.rainfall_mm)
    
    if temp > 30:
        weather_status = "Hot"
        weather_color = "#ef4444"
    elif temp < 15:
        weather_status = "Cold"
        weather_color = "#3b82f6"
    else:
        weather_status = "Moderate"
        weather_color = "#10b981"
    
    weather_details = f"{temp}°C, {rainfall}mm rain"
    
    # Health status based on disease alert
    disease_status = latest_data.disease_alert
    if disease_status == 'Presence':
        health_status = "Disease Alert"
        health_color = "#ef4444"
        health_details = "Disease detected in area"
    else:
        health_status = "Healthy"
        health_color = "#10b981"
        health_details = "No disease reported"
    
    return Response({
        'weather': {
            'status': weather_status,
            'details': weather_details,
            'color': weather_color,
            'temperature': temp,
            'rainfall': rainfall
        },
        'health': {
            'status': health_status,
            'details': health_details,
            'color': health_color,
            'disease_alert': disease_status
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def market_insights_chart(request):
    """Small donut chart for Market Insights card"""
    
    # Get demand distribution from recent data
    recent_data = MarketData.objects.order_by('-year', '-week')[:20]
    demand_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    
    for data in recent_data:
        demand_counts[data.market_demand] += 1
    
    total = sum(demand_counts.values())
    if total == 0:
        # Fallback data
        demand_counts = {'High': 30, 'Medium': 50, 'Low': 20}
        total = 100
    
    percentages = {k: round((v/total)*100) for k, v in demand_counts.items()}
    
    return Response({
        'chart_type': 'donut',
        'title': 'Demand Distribution',
        'data': [
            {'label': 'High Demand', 'value': percentages['High'], 'color': '#ef4444'},
            {'label': 'Medium Demand', 'value': percentages['Medium'], 'color': '#f59e0b'},
            {'label': 'Low Demand', 'value': percentages['Low'], 'color': '#10b981'}
        ],
        'center_text': f"{percentages['High']}%",
        'center_label': 'High Demand'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def business_insights_data(request):
    """Data for Business Insights card"""
    
    # Calculate profit potential based on demand levels
    recent_data = MarketData.objects.order_by('-year', '-week')[:12]
    
    if not recent_data:
        return Response({
            'current_profit_potential': 'Medium',
            'weekly_revenue_estimate': '450,000',
            'best_selling_days': 'Tuesday, Friday',
            'market_trend': 'Stable',
            'insights': [
                'High demand expected next week',
                'Market day sales up 15%',
                'Weather conditions favorable'
            ]
        })
    
    high_demand_weeks = len([d for d in recent_data if d.market_demand == 'High'])
    market_days = len([d for d in recent_data if d.market_day])
    
    # Calculate profit potential
    if high_demand_weeks >= 4:
        profit_potential = 'High'
        revenue_estimate = '650,000'
    elif high_demand_weeks >= 2:
        profit_potential = 'Medium'
        revenue_estimate = '450,000'
    else:
        profit_potential = 'Low'
        revenue_estimate = '280,000'
    
    # Market trend
    latest_3 = recent_data[:3]
    high_recent = len([d for d in latest_3 if d.market_demand == 'High'])
    if high_recent >= 2:
        trend = 'Growing'
    elif high_recent == 1:
        trend = 'Stable'
    else:
        trend = 'Declining'
    
    return Response({
        'current_profit_potential': profit_potential,
        'weekly_revenue_estimate': revenue_estimate,
        'best_selling_days': 'Tuesday, Friday' if market_days > 6 else 'Friday, Saturday',
        'market_trend': trend,
        'insights': [
            f'{high_demand_weeks} high-demand weeks recorded',
            f'Market days show {market_days}/12 activity',
            f'Trend is {trend.lower()} this month'
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def agricultural_tips(request):
    """Smart agricultural tips based on real market data and conditions"""
    
    # Get latest market data for contextual tips
    latest_data = MarketData.objects.order_by('-year', '-week').first()
    recent_predictions = Prediction.objects.order_by('-timestamp')[:10]
    
    # Analyze recent market trends
    recent_predictions = Prediction.objects.order_by('-timestamp')[:10]
    recent_high_demand = Prediction.objects.filter(predicted_demand='High').order_by('-timestamp')[:10]
    high_demand_weeks = recent_high_demand.count()
    avg_confidence = recent_predictions.aggregate(avg=Avg('confidence_score'))['avg'] or 0.5
    
    # Base tips that are always relevant
    base_tips = [
        {
            'icon': '💡',
            'text': 'Plant tomatoes during dry season for better yields',
            'priority': 'high'
        },
        {
            'icon': '🌱',
            'text': 'Use organic fertilizers to improve soil health',
            'priority': 'medium'
        }
    ]
    
    # Contextual tips based on data
    contextual_tips = []
    
    if latest_data:
        # Temperature-based tips
        if hasattr(latest_data, 'temperature_c') and latest_data.temperature_c:
            if float(latest_data.temperature_c) > 25:
                contextual_tips.append({
                    'icon': '🌡️',
                    'text': f'High temperature ({latest_data.temperature_c}°C) - increase irrigation frequency',
                    'priority': 'high'
                })
            elif float(latest_data.temperature_c) < 20:
                contextual_tips.append({
                    'icon': '❄️',
                    'text': 'Cool weather detected - protect young plants from cold',
                    'priority': 'medium'
                })
        
        # Rainfall-based tips
        if hasattr(latest_data, 'rainfall_mm') and latest_data.rainfall_mm:
            if float(latest_data.rainfall_mm) > 100:
                contextual_tips.append({
                    'icon': '🌧️',
                    'text': 'Heavy rainfall detected - ensure proper drainage',
                    'priority': 'high'
                })
            elif float(latest_data.rainfall_mm) < 20:
                contextual_tips.append({
                    'icon': '💧',
                    'text': 'Low rainfall - implement water conservation techniques',
                    'priority': 'high'
                })
        
        # Disease-based tips
        if hasattr(latest_data, 'disease_alert') and latest_data.disease_alert == 'Presence':
            contextual_tips.append({
                'icon': '🦠',
                'text': 'Disease alert active - apply preventive treatments immediately',
                'priority': 'critical'
            })
    
    # Market-based tips
    if high_demand_weeks >= 3:
        contextual_tips.append({
            'icon': '📈',
            'text': f'High demand trend ({high_demand_weeks}/10 weeks) - consider expanding production',
            'priority': 'high'
        })
    elif high_demand_weeks <= 1:
        contextual_tips.append({
            'icon': '📉',
            'text': 'Low demand period - focus on quality over quantity',
            'priority': 'medium'
        })
    
    # Confidence-based tips
    if avg_confidence > 0.8:
        contextual_tips.append({
            'icon': '🎯',
            'text': f'High prediction confidence ({int(avg_confidence*100)}%) - good time for planning',
            'priority': 'medium'
        })
    
    # Combine and prioritize tips
    all_tips = base_tips + contextual_tips
    
    # Sort by priority (critical > high > medium > low)
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    sorted_tips = sorted(all_tips, key=lambda x: priority_order.get(x['priority'], 3))
    
    # Return top 4 most relevant tips
    return Response({
        'tips': sorted_tips[:4],
        'last_updated': datetime.now().isoformat(),
        'data_source': 'real_time_analysis'
    })
