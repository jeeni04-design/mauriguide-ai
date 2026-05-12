from django.db import models


class WaterActivity(models.Model):
    CATEGORY_CHOICES = [
        ("niche", "Niche"),
        ("widespread", "Widespread"),
        ("underrated", "Underrated"),
    ]
    SEGMENT_CHOICES = [
        ("single", "Single"),
        ("couple", "Couple"),
        ("team", "Team"),
    ]
    
    activity = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES)
    location = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="water_activities/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Water Activity"
        verbose_name_plural = "Water Activities"
    
    def __str__(self):
        return f"{self.activity} - {self.location}"


class LandActivity(models.Model):
    CATEGORY_CHOICES = [
        ("niche", "Niche"),
        ("widespread", "Widespread"),
        ("underrated", "Underrated"),
    ]
    
    activity = models.CharField(max_length=200)
    place = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="land_activities/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Land Activity"
        verbose_name_plural = "Land Activities"
    
    def __str__(self):
        return f"{self.activity} - {self.place}"


class Hike(models.Model):
    DIFFICULTY_CHOICES = [
        (1, "1 - Easy"),
        (2, "2 - Moderate"),
        (3, "3 - Intermediate"),
        (4, "4 - Hard"),
        (5, "5 - Very Difficult"),
    ]
    
    trail_name = models.CharField(max_length=200)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    details = models.TextField()
    image = models.ImageField(upload_to="hikes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hike"
        verbose_name_plural = "Hikes"
    
    def __str__(self):
        return f"{self.trail_name} (Level {self.difficulty})"


class FoodOutlet(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20, blank=True)
    speciality = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="food_outlets/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Food Outlet"
        verbose_name_plural = "Food Outlets"
    
    def __str__(self):
        return f"{self.name} - {self.speciality}"


class Beach(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="beaches/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Beach"
        verbose_name_plural = "Beaches"
    
    def __str__(self):
        return self.name


class SiteToVisit(models.Model):
    place = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    location = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    why_visit = models.TextField()
    visitor_info = models.TextField(blank=True)
    best_time = models.CharField(max_length=200, blank=True)
    tips = models.TextField(blank=True)
    image = models.ImageField(upload_to="sites/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Site to Visit"
        verbose_name_plural = "Sites to Visit"
    
    def __str__(self):
        return self.place
