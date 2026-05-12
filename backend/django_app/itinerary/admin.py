from django.contrib import admin
from .models import Itinerary, ItineraryStop


class ItineraryStopInline(admin.TabularInline):
    model = ItineraryStop
    extra = 0
    fields = ['order', 'category', 'item_name', 'location', 'duration_hours', 'notes']


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'start_point', 'end_point', 'stop_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username', 'start_point', 'end_point']
    inlines = [ItineraryStopInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ItineraryStop)
class ItineraryStopAdmin(admin.ModelAdmin):
    list_display = ['itinerary', 'order', 'category', 'item_name', 'location']
    list_filter = ['category']
    search_fields = ['item_name', 'location']
