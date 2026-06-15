from django.apps import AppConfig


class InsightsConfig(AppConfig):
    name = "insights"
    verbose_name = "Insights & Analytics"

    def ready(self):
        """Register signal handlers when app is ready."""
        from insights import events, signals  # noqa
