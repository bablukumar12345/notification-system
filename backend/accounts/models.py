from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Stores each user's phone number and last activity time.

    Phone is needed for WhatsApp (with country code, e.g. 919876543210).
    last_seen_at drives the 'not logged in for 1 day / 1 week' triggers.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, default="")
    last_seen_at = models.DateTimeField(null=True, blank=True)
    inactive_1_day_sent_at = models.DateTimeField(null=True, blank=True)
    inactive_1_week_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
