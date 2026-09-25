from django.contrib import admin

from .models import NotificationLog, PushSubscription, Template, Trigger


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("trigger", "channel", "is_enabled", "updated_at")
    list_filter = ("channel", "is_enabled")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "trigger_code", "channel", "recipient", "status", "is_test")
    list_filter = ("channel", "status", "is_test")


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "player_id", "created_at")
