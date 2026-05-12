from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

User = get_user_model()


def _image_url(request, obj):
    """Return absolute image URL or None."""
    if obj.image:
        return request.build_absolute_uri(obj.image.url)
    return None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_places(request):
    """
    Returns all places from all 6 datasets with coordinates and image URLs.
    Used by the dashboard Discover section.
    """
    from datasets.models import Beach, FoodOutlet, SiteToVisit, WaterActivity, LandActivity, Hike

    places = []

    for b in Beach.objects.all():
        places.append({
            'id': f'beach_{b.id}', 'name': b.name, 'location': b.location,
            'latitude': b.latitude, 'longitude': b.longitude, 'category': 'beach',
            'description': b.description or '',
            'image_url': _image_url(request, b),
        })

    for f in FoodOutlet.objects.all():
        places.append({
            'id': f'food_{f.id}', 'name': f.name, 'location': f.location,
            'latitude': f.latitude, 'longitude': f.longitude, 'category': 'food',
            'description': f.description or '',
            'image_url': _image_url(request, f),
        })

    for s in SiteToVisit.objects.all():
        places.append({
            'id': f'site_{s.id}', 'name': s.place, 'location': s.location,
            'latitude': s.latitude, 'longitude': s.longitude, 'category': 'site',
            'description': s.why_visit or '',
            'image_url': _image_url(request, s),
        })

    for w in WaterActivity.objects.all():
        places.append({
            'id': f'water_{w.id}', 'name': w.activity, 'location': w.location,
            'latitude': w.latitude, 'longitude': w.longitude, 'category': 'water',
            'description': w.description or '',
            'image_url': _image_url(request, w),
        })

    for l in LandActivity.objects.all():
        places.append({
            'id': f'land_{l.id}', 'name': l.activity, 'location': l.place,
            'latitude': l.latitude, 'longitude': l.longitude, 'category': 'land',
            'description': l.description or '',
            'image_url': _image_url(request, l),
        })

    for h in Hike.objects.all():
        places.append({
            'id': f'hike_{h.id}', 'name': h.trail_name, 'location': 'Trail',
            'latitude': h.latitude, 'longitude': h.longitude, 'category': 'hike',
            'description': h.details or '',
            'image_url': _image_url(request, h),
        })

    return Response({'places': places, 'total': len(places)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    user = request.user
    return Response({'user_id': user.id, 'username': user.username, 'email': user.email,
                     'first_name': user.first_name, 'last_name': user.last_name, 'is_authenticated': True})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username,
                         'email': user.email, 'message': 'Login successful'})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({'id': user.id, 'username': user.username, 'email': user.email,
                     'first_name': user.first_name, 'last_name': user.last_name,
                     'date_joined': user.date_joined})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        if not username or not email or not password:
            return Response({'error': 'Please provide username, email, and password'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, email=email, password=password,
                                         first_name=first_name, last_name=last_name)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username,
                         'email': user.email, 'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback; print(traceback.format_exc())
        return Response({'error': f'Registration failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    return Response({'status': 'healthy', 'service': 'MauriGuide Django API'})