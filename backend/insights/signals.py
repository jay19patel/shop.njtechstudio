from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Any

from store.models import Product, Category
from insights.models import ProductEmbedding, CategoryEmbedding
from insights.services.embeddings import EmbeddingService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def generate_product_embedding(
    sender: Any,
    instance: Product,
    created: bool,
    **kwargs: Any,
) -> None:
    """Auto-generate embedding when product is created/updated."""
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


@receiver(post_save, sender=Category)
def generate_category_embedding(
    sender: Any,
    instance: Category,
    created: bool,
    **kwargs: Any,
) -> None:
    """Auto-generate embedding when category is created/updated."""
    try:
        embedding_text = f"{instance.name} {instance.description}"

        service = EmbeddingService()
        vector = service.generate_embedding(embedding_text)

        if vector is None:
            logger.warning(f"Could not generate embedding for category {instance.id}")
            return

        CategoryEmbedding.objects.update_or_create(
            category=instance,
            defaults={
                'embedding_vector': vector,
            }
        )

        logger.info(f"Generated embedding for category {instance.id}: {instance.name}")

    except Exception as e:
        logger.error(f"Error generating embedding for category {instance.id}: {str(e)}")
