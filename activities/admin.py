from django.contrib import admin
from .models import Category, Activity, Consumption

class ConsumptionInline(admin.TabularInline):
    model = Consumption
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'user', 'favorite', 'created_at']
    list_filter = ['category', 'favorite', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    date_hierarchy = 'created_at'
    inlines = [ConsumptionInline]

@admin.register(Consumption)
class ConsumptionAdmin(admin.ModelAdmin):
    list_display = ['activity', 'consumed_at']
    list_filter = ['consumed_at']
    search_fields = ['activity__name', 'description', 'ingredients']
    date_hierarchy = 'consumed_at' 