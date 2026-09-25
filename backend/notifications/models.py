from django.contrib.auth.models import User
from django.db import models


class Channel(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "Email"
    WEBPUSH = "webpush", "Web Push"


class Trigger(models.Model):
    """One row of the admin table: any event that should send a notification."""

    code = models.SlugField(max_length=64, unique=True)  # e.g. login, logout
    name = models.CharField(max_length=120)  # e.g. "Login"
    description = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Template(models.Model):
    """One cell of the admin table: a template for one trigger on one channel."""

    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name="templates")
    channel = models.CharField(max_length=16, choices=Channel.choices)

    # Email: subject + body. Web Push: title + body. WhatsApp: body (or template name).
    subject = models.CharField(max_length=200, blank=True, default="")
    title = models.CharField(max_length=200, blank=True, default="")
    body = models.TextField(blank=True, default="")

    # Name of an approved WhatsApp Cloud API template (optional).
    # Leave it empty to send a plain text message (works inside the 24h session window).
    whatsapp_template_name = models.CharField(max_length=120, blank=True, default="")
    whatsapp_language = models.CharField(max_length=10, blank=True, default="en_US")

    # Variable mapping, e.g. {"name": "user.first_name", "site": "MyApp"}
    variables = models.JSONField(default=dict, blank=True)

    is_enabled = models.BooleanField(default=True)  # on / off toggle
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("trigger", "channel")
        ordering = ["trigger_id", "channel"]

    def __str__(self):
        return f"{self.trigger.code}:{self.channel}"


class PushSubscription(models.Model):
    """Holds the OneSignal subscription id created when a browser subscribes."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="push_subscriptions", null=True, blank=True
    )
    player_id = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user or 'anon'} -> {self.player_id[:12]}"


class NotificationLog(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    trigger_code = models.CharField(max_length=64)
    channel = models.CharField(max_length=16, choices=Channel.choices)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.CharField(max_length=200, blank=True, default="")
    rendered_subject = models.CharField(max_length=250, blank=True, default="")
    rendered_body = models.TextField(blank=True, default="")
    status = models.CharField(max_length=10, choices=Status.choices)
    is_test = models.BooleanField(default=False)
    provider_response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.trigger_code}/{self.channel} = {self.status}"
