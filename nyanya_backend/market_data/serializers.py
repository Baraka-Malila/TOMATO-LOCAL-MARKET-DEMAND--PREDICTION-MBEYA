"""
Market Data Serializers
"""

from rest_framework import serializers
from .models import MarketData, DataSource


class MarketDataSerializer(serializers.ModelSerializer):
    """Serializer for MarketData model"""
    
    is_high_demand = serializers.ReadOnlyField()
    demand_trend = serializers.ReadOnlyField()
    
    class Meta:
        model = MarketData
        fields = [
            'id',
            'week',
            'year', 
            'month',
            'rainfall_mm',
            'temperature_c',
            'market_day',
            'school_open',
            'disease_alert',
            'last_week_demand',
            'market_demand',
            'source',
            'created_at',
            'updated_at',
            'is_high_demand',
            'demand_trend',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarketDataListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing market data"""
    
    demand_trend = serializers.ReadOnlyField()
    
    class Meta:
        model = MarketData
        fields = [
            'id',
            'week',
            'year',
            'month', 
            'market_demand',
            'last_week_demand',
            'demand_trend',
            'created_at',
        ]


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model"""
    
    needs_update = serializers.ReadOnlyField()
    
    class Meta:
        model = DataSource
        fields = [
            'id',
            'name',
            'url',
            'description',
            'is_active',
            'last_fetch',
            'fetch_frequency',
            'created_at',
            'updated_at',
            'needs_update',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_fetch']
