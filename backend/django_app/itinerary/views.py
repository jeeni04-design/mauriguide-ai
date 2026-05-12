from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Itinerary, ItineraryStop
from .serializers import ItinerarySerializer, ItineraryCreateSerializer, ItineraryStopSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def itinerary_list(request):
    if request.method == 'GET':
        itineraries = Itinerary.objects.filter(user=request.user)
        serializer = ItinerarySerializer(itineraries, many=True)
        return Response(serializer.data)
    serializer = ItineraryCreateSerializer(data=request.data)
    if serializer.is_valid():
        itinerary = serializer.save(user=request.user)
        return Response(ItinerarySerializer(itinerary).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def itinerary_detail(request, pk):
    try:
        itinerary = Itinerary.objects.get(pk=pk, user=request.user)
    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ItinerarySerializer(itinerary).data)

    if request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = ItineraryCreateSerializer(itinerary, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(ItinerarySerializer(itinerary).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    itinerary.delete()
    return Response({'message': 'Itinerary deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_stop(request, pk):
    try:
        itinerary = Itinerary.objects.get(pk=pk, user=request.user)
    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    # ── FIX: item_id can be 0 (falsy) so check for None explicitly ──
    required = ['category', 'item_name', 'location']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return Response(
            {'error': f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # item_id defaults to 0 if not provided or 0
    item_id = data.get('item_id', 0)
    if item_id is None:
        item_id = 0

    print('add_stop data:', dict(data))
    stop = ItineraryStop.objects.create(
        itinerary=itinerary,
        category=data.get('category'),
        item_id=item_id,
        item_name=data.get('item_name'),
        location=data.get('location'),
        order=itinerary.ordered_stops.count() + 1,
        notes=data.get('notes', ''),
        duration_hours=data.get('duration_hours', 2.0)
    )

    return Response(ItinerarySerializer(itinerary).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_stop(request, pk, stop_id):
    try:
        itinerary = Itinerary.objects.get(pk=pk, user=request.user)
        stop = ItineraryStop.objects.get(id=stop_id, itinerary=itinerary)
    except (Itinerary.DoesNotExist, ItineraryStop.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    stop.delete()

    with transaction.atomic():
        for idx, remaining in enumerate(itinerary.ordered_stops.all(), start=1):
            if remaining.order != idx:
                remaining.order = idx
                remaining.save(update_fields=['order'])

    return Response(ItinerarySerializer(itinerary).data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_stop(request, pk, stop_id):
    try:
        itinerary = Itinerary.objects.get(pk=pk, user=request.user)
        stop = ItineraryStop.objects.get(id=stop_id, itinerary=itinerary)
    except (Itinerary.DoesNotExist, ItineraryStop.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    editable_fields = ['notes', 'duration_hours']
    updated = []
    for field in editable_fields:
        if field in request.data:
            setattr(stop, field, request.data[field])
            updated.append(field)

    if updated:
        stop.save(update_fields=updated)

    return Response(ItineraryStopSerializer(stop).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_stops(request, pk):
    try:
        itinerary = Itinerary.objects.get(pk=pk, user=request.user)
    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=status.HTTP_404_NOT_FOUND)

    order = request.data.get('order', [])
    if not order:
        return Response({'error': 'No order provided'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        for idx, stop_id in enumerate(order, start=1):
            ItineraryStop.objects.filter(id=stop_id, itinerary=itinerary).update(order=idx)

    return Response(ItinerarySerializer(itinerary).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """Return recommended places based on user preferences."""
    from datasets.models import Beach, FoodOutlet, WaterActivity, LandActivity, SiteToVisit, Hike
    import random

    category = request.GET.get('category', 'all')
    limit = int(request.GET.get('limit', 10))

    places = []
    if category in ('all', 'beach'):
        for b in Beach.objects.all():
            places.append({'name': b.name, 'category': 'beach', 'location': b.location, 'latitude': b.latitude, 'longitude': b.longitude})
    if category in ('all', 'food'):
        for f in FoodOutlet.objects.all():
            places.append({'name': f.name, 'category': 'food', 'location': f.location, 'latitude': f.latitude, 'longitude': f.longitude})
    if category in ('all', 'water'):
        for w in WaterActivity.objects.all():
            places.append({'name': w.activity, 'category': 'water', 'location': w.location, 'latitude': w.latitude, 'longitude': w.longitude})
    if category in ('all', 'land'):
        for l in LandActivity.objects.all():
            places.append({'name': l.activity, 'category': 'land', 'location': l.place, 'latitude': l.latitude, 'longitude': l.longitude})
    if category in ('all', 'site'):
        for s in SiteToVisit.objects.all():
            places.append({'name': s.place, 'category': 'site', 'location': s.location, 'latitude': s.latitude, 'longitude': s.longitude})
    if category in ('all', 'hike'):
        for h in Hike.objects.all():
            places.append({'name': h.trail_name, 'category': 'hike', 'location': 'Trail', 'latitude': h.latitude, 'longitude': h.longitude})

    random.shuffle(places)
    return Response({'recommendations': places[:limit], 'total': len(places)})