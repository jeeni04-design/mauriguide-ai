from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, ConsentLog, UserActivity
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ConsentUpdateSerializer,
    AccountDeletionSerializer,
)


def get_client_ip(request):
    x = request.META.get("HTTP_X_FORWARDED_FOR")
    return x.split(",")[0] if x else request.META.get("REMOTE_ADDR")


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserActivity.objects.create(
            user=user,
            activity_type="registration",
            description=f"Registered as {user.user_type}",
            ip_address=get_client_ip(request)
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Registration successful!",
            "user": UserProfileSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Provide username and password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    if not user.is_active:
        return Response(
            {"error": "Account deactivated"},
            status=status.HTTP_403_FORBIDDEN
        )

    user.last_login_ip = get_client_ip(request)
    user.last_login = timezone.now()
    user.save()

    UserActivity.objects.create(
        user=user,
        activity_type="login",
        description="User logged in",
        ip_address=get_client_ip(request)
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login successful!",
        "user": UserProfileSerializer(user).data,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        rt = request.data.get("refresh")
        if rt:
            RefreshToken(rt).blacklist()
        UserActivity.objects.create(
            user=request.user,
            activity_type="logout",
            description="User logged out",
            ip_address=get_client_ip(request)
        )
    except Exception:
        pass
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == "GET":
        return Response(UserProfileSerializer(request.user).data)
    s = UserProfileSerializer(request.user, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response({"message": "Updated", "user": s.data})
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_consent(request):
    s = ConsentUpdateSerializer(data=request.data)
    if s.is_valid():
        u = request.user
        for ct, v in s.validated_data.items():
            setattr(u, ct, v)
            ConsentLog.objects.create(
                user=u,
                consent_type=ct.replace("_consent", ""),
                granted=v,
                ip_address=get_client_ip(request)
            )
        u.save()
        return Response({"message": "Consent updated"}, status=status.HTTP_200_OK)
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_account_deletion(request):
    s = AccountDeletionSerializer(data=request.data)
    if s.is_valid():
        request.user.request_account_deletion()
        return Response(
            {"message": "Deletion requested per DPA 2017"},
            status=status.HTTP_200_OK
        )
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    u = request.user
    return Response({
        "user_information": UserProfileSerializer(u).data,
        "consent_history": list(ConsentLog.objects.filter(user=u).values()),
        "activity_history": list(UserActivity.objects.filter(user=u).values()),
        "export_date": timezone.now().isoformat(),
    }, status=status.HTTP_200_OK)
