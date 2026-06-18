from django.core.management.base import BaseCommand, CommandError
from typing import Any
from insights.kafka import start_listener
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command to run the background Kafka consumer daemon."""

    help = 'Runs the Kafka event listener to process e-commerce metrics and track interests.'

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS('Starting Kafka consumer daemon...'))
        try:
            start_listener()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Consumer stopped by user.'))
        except Exception as e:
            logger.error(f"Error in Kafka consumer management command: {str(e)}")
            raise CommandError(f"Consumer exited with error: {str(e)}")
