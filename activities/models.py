from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

User = get_user_model()

class ActivityCategory(models.Model):
    """Model for activity categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, default="blue")
    
    class Meta:
        verbose_name_plural = "Activity Categories"
        ordering = ["name"]
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    """Base model for all activities"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE, related_name="activities")
    description = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Activities"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("activities:activity_detail", kwargs={"pk": self.pk})

class Consumption(models.Model):
    """Model for consumption activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="consumptions")
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True, help_text="Enter ingredients, one per line")
    consumed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ["-consumed_at"]
    
    def __str__(self):
        return f"{self.activity.name} consumed at {self.consumed_at}" 