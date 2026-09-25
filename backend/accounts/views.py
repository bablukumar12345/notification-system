from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from notifications.dispatcher import fire_trigger

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


def _auth_payload(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, "user": UserSerializer(user).data}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    user.profile.last_seen_at = timezone.now()
    user.profile.save()

    # Trigger: signup
    results = fire_trigger("signup", user=user)

    payload = _auth_payload(user)
    payload["notifications"] = results
    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response({"detail": "Incorrect username or password."}, status=400)

    profile = user.profile
    profile.last_seen_at = timezone.now()
    profile.inactive_1_day_sent_at = None
    profile.inactive_1_week_sent_at = None
    profile.save()

    # Trigger: login
    results = fire_trigger("login", user=user)

    payload = _auth_payload(user)
    payload["notifications"] = results
    return Response(payload)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    # Trigger: logout (sent before the token is deleted)
    results = fire_trigger("logout", user=user)

    user.profile.last_seen_at = timezone.now()
    user.profile.save()
    Token.objects.filter(user=user).delete()
    return Response({"detail": "Logged out", "notifications": results})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "PATCH":
        phone = request.data.get("phone")
        if phone is not None:
            user.profile.phone = phone
            user.profile.save()
        email = request.data.get("email")
        if email:
            user.email = email
            user.save(update_fields=["email"])
    user.profile.last_seen_at = timezone.now()
    user.profile.save(update_fields=["last_seen_at"])
    return Response(UserSerializer(user).data)
