"""App configuration for produits."""

from django.apps import AppConfig


class ProduitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'produits'

    def ready(self):
        """Import signals when the app is ready."""
        import produits.signals  # noqa
