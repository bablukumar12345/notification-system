from rest_framework import serializers

from .models import Channel, NotificationLog, PushSubscription, Template, Trigger


class TemplateSerializer(serializers.ModelSerializer):
    trigger_code = serializers.CharField(source="trigger.code", read_only=True)

    class Meta:
        model = Template
        fields = [
            "id",
            "trigger",
            "trigger_code",
            "channel",
            "subject",
            "title",
            "body",
            "whatsapp_template_name",
            "whatsapp_language",
            "variables",
            "is_enabled",
            "updated_at",
        ]

    def validate(self, attrs):
        channel = attrs.get("channel") or getattr(self.instance, "channel", None)
        body = attrs.get("body", getattr(self.instance, "body", ""))
        subject = attrs.get("subject", getattr(self.instance, "subject", ""))
        title = attrs.get("title", getattr(self.instance, "title", ""))

        if channel == Channel.EMAIL and not subject.strip():
            raise serializers.ValidationError({"subject": "A subject is required for email."})
        if channel == Channel.WEBPUSH and not title.strip():
            raise serializers.ValidationError({"title": "A title is required for web push."})
        if not body.strip() and not attrs.get("whatsapp_template_name"):
            raise serializers.ValidationError({"body": "The message body cannot be empty."})
        return attrs


class TriggerSerializer(serializers.ModelSerializer):
    templates = TemplateSerializer(many=True, read_only=True)
    channels = serializers.SerializerMethodField()

    class Meta:
        model = Trigger
        fields = ["id", "code", "name", "description", "is_active", "templates", "channels"]

    def get_channels(self, obj):
        """Channel keyed dict for the admin table: {whatsapp: {...}|null, ...}"""
        data = {c.value: None for c in Channel}
        for template in obj.templates.all():
            data[template.channel] = TemplateSerializer(template).data
        return data


class NotificationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", default="", read_only=True)

    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "trigger_code",
            "channel",
            "username",
            "recipient",
            "rendered_subject",
            "rendered_body",
            "status",
            "is_test",
            "provider_response",
            "created_at",
        ]


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ["id", "player_id", "created_at"]
