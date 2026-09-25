from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("triggers", views.TriggerViewSet, basename="trigger")
router.register("templates", views.TemplateViewSet, basename="template")
router.register("logs", views.NotificationLogViewSet, basename="log")

urlpatterns = [
    path("", include(router.urls)),
    path("channels/", views.channel_list, name="channels"),
    path("push/subscribe/", views.subscribe_push, name="push-subscribe"),
    path("triggers-fire/<slug:code>/", views.fire_custom_trigger, name="fire-trigger"),
    path("cron/inactivity/", views.cron_inactivity, name="cron-inactivity"),
]
