from django.core.management.base import BaseCommand

from notifications.tasks import run_inactivity_check


class Command(BaseCommand):
    help = "Sends the 'not logged in 1 day / 1 week' notifications to inactive users."

    def handle(self, *args, **options):
        summary = run_inactivity_check()
        self.stdout.write(
            self.style.SUCCESS(
                f"Checked {summary['checked']} users, sent {len(summary['sent'])} notifications."
            )
        )
