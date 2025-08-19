"""
Prediction Models
"""

from django.db import models
from django.utils import timezone


class Prediction(models.Model):
    """Model to store prediction results"""
    
    timestamp = models.DateTimeField(default=timezone.now)
    week = models.PositiveIntegerField()
    year = models.PositiveIntegerField(default=timezone.now().year)
    
    predicted_demand = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low Demand'),
            ('Medium', 'Medium Demand'),
            ('High', 'High Demand'),
        ]
    )
    
    confidence_score = models.FloatField()
    rainfall_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Week {self.week}, {self.year} - {self.predicted_demand} ({self.confidence_score:.2f})"
