"""
Market Data Models
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class MarketData(models.Model):
    """Model to store weekly market data"""
    
    week = models.PositiveIntegerField()
    year = models.PositiveIntegerField(default=timezone.now().year)
    month = models.CharField(max_length=20)
    
    rainfall_mm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2)
    
    market_day = models.BooleanField(default=False)
    school_open = models.BooleanField(default=True)
    
    disease_alert = models.CharField(
        max_length=20,
        choices=[
            ('Presence', 'Disease Present'),
            ('Absence', 'No Disease'),
        ],
        default='Absence'
    )
    
    last_week_demand = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low Demand'),
            ('Medium', 'Medium Demand'),
            ('High', 'High Demand'),
        ]
    )
    market_demand = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low Demand'),
            ('Medium', 'Medium Demand'),
            ('High', 'High Demand'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='manual_upload')
    
    class Meta:
        ordering = ['-year', '-week']
        unique_together = ['year', 'week']
        
    def __str__(self):
        return f"Week {self.week}, {self.year} - {self.market_demand} Demand"
    
    @property
    def is_high_demand(self):
        return self.market_demand == 'High'
    
    @property
    def demand_trend(self):
        demand_levels = {'Low': 1, 'Medium': 2, 'High': 3}
        current = demand_levels.get(self.market_demand, 2)
        previous = demand_levels.get(self.last_week_demand, 2)
        
        if current > previous:
            return 'Increasing'
        elif current < previous:
            return 'Decreasing'
        else:
            return 'Stable'


class DataSource(models.Model):
    """Model to track different data sources"""
    
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_fetch = models.DateTimeField(blank=True, null=True)
    fetch_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('manual', 'Manual'),
        ],
        default='weekly'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    @property
    def needs_update(self):
        if not self.is_active or not self.last_fetch:
            return True
            
        from datetime import timedelta
        now = timezone.now()
        
        frequency_map = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
        }
        
        if self.fetch_frequency in frequency_map:
            time_since_last_fetch = now - self.last_fetch
            return time_since_last_fetch >= frequency_map[self.fetch_frequency]
        
        return False
