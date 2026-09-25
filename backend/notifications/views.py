from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .dispatcher import build_context, fire_trigger, send_on_channel
from .models import Channel, NotificationLog, PushSubscription, Template, Trigger
from .serializers import (
    NotificationLogSerializer,
    PushSubscriptionSerializer,
    TemplateSerializer,
    TriggerSerializer,
)
from .tasks import run_inactivity_check


class TriggerViewSet(viewsets.ModelViewSet):
    """Rows of the admin table. Only staff users can manage these."""

    queryset = Trigger.objects.prefetch_related("templates").all()
    serializer_class = TriggerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="fire")
    def fire(self, request, pk=None):
        """Fire a trigger manually from the admin panel (demo and testing)."""
        trigger = self.get_object()
        results = fire_trigger(trigger.code, user=request.user)
        return Response({"trigger": trigger.code, "results": results})


class TemplateViewSet(viewsets.ModelViewSet):
    """Cells of the admin table."""

    queryset = Template.objects.select_related("trigger").all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        trigger_id = self.request.query_params.get("trigger")
        channel = self.request.query_params.get("channel")
        if trigger_id:
            qs = qs.filter(trigger_id=trigger_id)
        if channel:
            qs = qs.filter(channel=channel)
        return qs

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle(self, request, pk=None):
        template = self.get_object()
        value = request.data.get("is_enabled")
        template.is_enabled = (not template.is_enabled) if value is None else bool(value)
        template.save(update_fields=["is_enabled", "updated_at"])
        return Response(TemplateSerializer(template).data)

    @action(detail=True, methods=["post"], url_path="test-send")
    def test_send(self, request, pk=None):
        """Sends a test message. Pass phone / email / player_id in the body,
        otherwise the signed-in admin's own details are used."""
        template = self.get_object()
        user = request.user
        context = build_context(user)

        overrides = {}
        if request.data.get("phone"):
            overrides["phone"] = request.data["phone"]
            context["phone"] = request.data["phone"]
        if request.data.get("email"):
            overrides["email"] = request.data["email"]
            context["email"] = request.data["email"]
        if request.data.get("player_id"):
            overrides["player_ids"] = [request.data["player_id"]]

        result = send_on_channel(
            template, user=user, context=context, is_test=True, overrides=overrides
        )
        return Response(
            {"channel": template.channel, **result.as_dict()},
            status=200 if result.ok else 400,
        )


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.select_related("user").all()[:300]
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAdminUser]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe_push(request):
    """Save the OneSignal subscription id so push can reach this user."""
    player_id = (request.data.get("player_id") or "").strip()
    if not player_id:
        return Response({"detail": "player_id is required."}, status=400)

    sub, _ = PushSubscription.objects.update_or_create(
        player_id=player_id, defaults={"user": request.user}
    )
    return Response(PushSubscriptionSerializer(sub).data, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fire_custom_trigger(request, code):
    """Any event on the site can fire a trigger through this endpoint.
    e.g. POST /api/triggers-fire/order_placed/"""
    request.user.profile.last_seen_at = timezone.now()
    request.user.profile.save(update_fields=["last_seen_at"])
    results = fire_trigger(code, user=request.user, extra=request.data.get("variables"))
    return Response({"trigger": code, "results": results})


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def cron_inactivity(request):
    """A Render cron job or UptimeRobot hits this to run the inactive-user triggers.
    Security: ?secret=<CRON_SECRET>"""
    secret = request.query_params.get("secret") or request.data.get("secret")
    if secret != settings.CRON_SECRET:
        return Response({"detail": "Invalid secret."}, status=403)
    summary = run_inactivity_check()
    return Response(summary)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def channel_list(_request):
    return Response([{"value": c.value, "label": c.label} for c in Channel])
