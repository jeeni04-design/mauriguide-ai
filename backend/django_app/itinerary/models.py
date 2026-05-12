from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Itinerary(models.Model):
    """User's saved trip itineraries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    name = models.CharField(max_length=200, help_text='e.g., My 3-Day Beach Adventure')
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    stops = models.JSONField(default=list, help_text='List of stops with details')
    notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=False, help_text='Share with other users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Itinerary'
        verbose_name_plural = 'Itineraries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def stop_count(self):
        return len(self.stops) if self.stops else 0


class ItineraryStop(models.Model):
    """Individual stops within an itinerary"""
    CATEGORY_CHOICES = [
        ('beach', 'Beach'),
        ('water', 'Water Activity'),
        ('land', 'Land Activity'),
        ('hike', 'Hike'),
        ('food', 'Food Outlet'),
        ('site', 'Site to Visit'),
    ]
    
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='ordered_stops')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    item_id = models.IntegerField(help_text='ID of the beach/activity/site')
    item_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    duration_hours = models.FloatField(default=2.0, help_text='Estimated time to spend')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.order}. {self.item_name}"
