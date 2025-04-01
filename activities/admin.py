from django.contrib import admin
from .models import ActivityCategory, Activity, Consumption

class ConsumptionInline(admin.TabularInline):
    model = Consumption
    extra = 1

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user', 'created_at', 'favorite')
    list_filter = ('category', 'favorite', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    inlines = [ConsumptionInline]

@admin.register(Consumption)
class ConsumptionAdmin(admin.ModelAdmin):
    list_display = ('activity', 'consumed_at')
    list_filter = ('consumed_at',)
    search_fields = ('activity__name', 'description', 'ingredients')
    date_hierarchy = 'consumed_at' 