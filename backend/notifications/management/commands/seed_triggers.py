import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from notifications.models import Channel, Template, Trigger

TRIGGERS = [
    ("login", "Login", "User signs in on the website"),
    ("logout", "Logout", "User signs out"),
    ("signup", "Signup", "A new account is created"),
    ("not_logged_in_1_day", "Not logged in for 1 day", "No visit in the last 24 hours"),
    ("not_logged_in_1_week", "Not logged in for 1 week", "No visit in the last 7 days"),
    ("password_reset", "Password reset", "User asks to reset their password"),
    ("order_placed", "Order placed", "User completes a purchase"),
]

DEFAULT_TEMPLATES = {
    "login": {
        Channel.WHATSAPP: {"body": "Welcome back, {{name}}! You just signed in to {{site}}."},
        Channel.EMAIL: {
            "subject": "You logged in successfully",
            "body": "Hi {{name}},\n\nYou signed in successfully. If this wasn't you, change your password right away.\n\n- {{site}}",
        },
        Channel.WEBPUSH: {"title": "Welcome back!", "body": "Good to see you again, {{name}}."},
    },
    "logout": {
        Channel.WHATSAPP: {"body": "Bye {{name}}, you have signed out of {{site}}."},
        Channel.EMAIL: {
            "subject": "You signed out",
            "body": "Hi {{name}},\n\nYou just signed out. See you next time.\n\n- {{site}}",
        },
        Channel.WEBPUSH: {"title": "Signed out", "body": "See you soon, {{name}}."},
    },
    "not_logged_in_1_week": {
        Channel.WHATSAPP: {"body": "We miss you, {{name}}! It has been a week since your last visit."},
        Channel.EMAIL: {
            "subject": "It's been a week",
            "body": "Hi {{name}},\n\nIt has been seven days since your last visit. Come back and see what's new.\n\n- {{site}}",
        },
        Channel.WEBPUSH: {"title": "Come visit us again", "body": "{{name}}, it's been a week!"},
    },
}


class Command(BaseCommand):
    help = "Creates the default triggers, sample templates and an admin user."

    def handle(self, *args, **options):
        for code, name, desc in TRIGGERS:
            Trigger.objects.get_or_create(
                code=code, defaults={"name": name, "description": desc}
            )
        self.stdout.write(self.style.SUCCESS(f"{len(TRIGGERS)} triggers ready."))

        for code, channels in DEFAULT_TEMPLATES.items():
            trigger = Trigger.objects.get(code=code)
            for channel, data in channels.items():
                Template.objects.get_or_create(trigger=trigger, channel=channel, defaults=data)
        self.stdout.write(self.style.SUCCESS("Sample templates ready."))

        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin12345")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin created: {username} / {password}"))
        else:
            self.stdout.write("Admin user already exists.")
