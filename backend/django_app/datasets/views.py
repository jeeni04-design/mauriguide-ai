from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import WaterActivity, LandActivity, Hike, FoodOutlet, Beach, SiteToVisit
from .serializers import (
    WaterActivitySerializer,
    LandActivitySerializer,
    HikeSerializer,
    FoodOutletSerializer,
    BeachSerializer,
    SiteToVisitSerializer
)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_datasets(request):
    """
    Get all datasets for map display
    Returns categorized data with colors for map markers
    """
    data = {
        "water_activities": {
            "data": WaterActivitySerializer(WaterActivity.objects.all(), many=True).data,
            "color": "blue",
            "icon": "💧"
        },
        "land_activities": {
            "data": LandActivitySerializer(LandActivity.objects.all(), many=True).data,
            "color": "green",
            "icon": "🌿"
        },
        "hikes": {
            "data": HikeSerializer(Hike.objects.all(), many=True).data,
            "color": "green",
            "icon": "🥾"
        },
        "food_outlets": {
            "data": FoodOutletSerializer(FoodOutlet.objects.all(), many=True).data,
            "color": "purple",
            "icon": "🍽️"
        },
        "beaches": {
            "data": BeachSerializer(Beach.objects.all(), many=True).data,
            "color": "lightblue",
            "icon": "🏖️"
        },
        "sites": {
            "data": SiteToVisitSerializer(SiteToVisit.objects.all(), many=True).data,
            "color": "gold",
            "icon": "📍"
        }
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_water_activities(request):
    activities = WaterActivity.objects.all()
    serializer = WaterActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_land_activities(request):
    activities = LandActivity.objects.all()
    serializer = LandActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_hikes(request):
    hikes = Hike.objects.all()
    serializer = HikeSerializer(hikes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_food_outlets(request):
    outlets = FoodOutlet.objects.all()
    serializer = FoodOutletSerializer(outlets, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_beaches(request):
    beaches = Beach.objects.all()
    serializer = BeachSerializer(beaches, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_sites(request):
    sites = SiteToVisit.objects.all()
    serializer = SiteToVisitSerializer(sites, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_locations(request):
    """
    Search across all datasets
    """
    query = request.GET.get("q", "").lower()
    
    if not query:
        return Response({"error": "Query parameter 'q' is required"}, status=400)
    
    results = []
    
    # Search water activities
    for item in WaterActivity.objects.filter(activity__icontains=query):
        results.append({
            "type": "water_activity",
            "name": item.activity,
            "location": item.location,
            "lat": item.latitude,
            "lon": item.longitude,
            "color": "blue"
        })
    
    # Search beaches
    for item in Beach.objects.filter(name__icontains=query):
        results.append({
            "type": "beach",
            "name": item.name,
            "location": item.location,
            "lat": item.latitude,
            "lon": item.longitude,
            "color": "lightblue"
        })
    
    # Search sites
    for item in SiteToVisit.objects.filter(place__icontains=query):
        results.append({
            "type": "site",
            "name": item.place,
            "location": item.location,
            "lat": item.latitude,
            "lon": item.longitude,
            "color": "gold"
        })
    
    # Search food outlets
    for item in FoodOutlet.objects.filter(name__icontains=query):
        results.append({
            "type": "food",
            "name": item.name,
            "location": item.location,
            "lat": item.latitude,
            "lon": item.longitude,
            "color": "purple"
        })
    
    return Response({"results": results, "count": len(results)})
