from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Product
from insights.models import ProductEmbedding
from insights.utils import EmbeddingService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def generate_product_embedding(sender, instance, created, **kwargs):
    """Auto-generate embedding when product is created/updated"""
    try:
        embedding_text = f"{instance.name} {instance.description}"

        service = EmbeddingService()
        vector = service.generate_embedding(embedding_text)

        if vector is None:
            logger.warning(f"Could not generate embedding for product {instance.id}")
            return

        ProductEmbedding.objects.update_or_create(
            product=instance,
            defaults={
                'embedding_vector': vector,
                'embedding_source': 'ollama',
                'description': f'Auto-generated for: {instance.name}'
            }
        )

        logger.info(f"Generated embedding for product {instance.id}: {instance.name}")

    except Exception as e:
        logger.error(f"Error generating embedding for product {instance.id}: {str(e)}")
