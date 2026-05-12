from rest_framework import serializers
from .models import WaterActivity, LandActivity, Hike, FoodOutlet, Beach, SiteToVisit


class WaterActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterActivity
        fields = '__all__'


class LandActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LandActivity
        fields = '__all__'


class HikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hike
        fields = '__all__'


class FoodOutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOutlet
        fields = '__all__'


class BeachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beach
        fields = '__all__'


class SiteToVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteToVisit
        fields = '__all__'
