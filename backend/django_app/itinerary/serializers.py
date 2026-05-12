from rest_framework import serializers
from .models import Itinerary, ItineraryStop


class ItineraryStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryStop
        fields = [
            'id', 'itinerary', 'category', 'item_id', 'item_name',
            'location', 'order', 'notes', 'duration_hours'
        ]
        read_only_fields = ['itinerary']


class ItinerarySerializer(serializers.ModelSerializer):
    ordered_stops = ItineraryStopSerializer(many=True, read_only=True)
    stop_count = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = [
            'id', 'name', 'start_point', 'end_point',
            'start_date', 'end_date', 'stops', 'notes',
            'is_public', 'created_at', 'updated_at',
            'ordered_stops', 'stop_count'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_stop_count(self, obj):
        return obj.ordered_stops.count()


class ItineraryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = [
            'name', 'start_point', 'end_point',
            'start_date', 'end_date', 'stops', 'notes', 'is_public'
        ]
