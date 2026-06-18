"""Product-related event handlers: view, like, unlike."""
import logging
from typing import Any
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import HttpRequest

from store.models import Like
from store.signals import product_viewed
from insights.kafka import get_producer
from insights.services.request_parser import RequestParserService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Like)
def track_product_like(
    sender: Any,
    instance: Like,
    created: bool,
    **kwargs: Any,
) -> None:
    """Track product like event when a Like object is created and publish it to Kafka."""
    if created:
        try:
            producer = get_producer()
            user_info = {
                'email': instance.user.email,
                'name': instance.user.first_name or instance.user.username,
                'ip_address': None,
                'user_agent': None,
            }
            producer.send_product_liked(
                user_id=instance.user.id,
                product_id=instance.product.id,
                product_name=instance.product.name,
                user_info=user_info,
            )
            logger.info("product_liked_signal",
                        extra={"product_id": instance.product.id, "user_id": instance.user.id})
        except Exception as e:
            logger.error("failed_to_track_product_like",
                         extra={"product_id": instance.product.id, "error": str(e)})


@receiver(post_delete, sender=Like)
def track_product_unlike(
    sender: Any,
    instance: Like,
    **kwargs: Any,
) -> None:
    """Track product unlike event when a Like object is deleted and publish it to Kafka."""
    try:
        producer = get_producer()
        user_info = {
            'email': instance.user.email,
            'name': instance.user.first_name or instance.user.username,
            'ip_address': None,
            'user_agent': None,
        }
        producer.send_product_unliked(
            user_id=instance.user.id,
            product_id=instance.product.id,
            product_name=instance.product.name,
            user_info=user_info,
        )
        logger.info("product_unliked_signal",
                    extra={"product_id": instance.product.id, "user_id": instance.user.id})
    except Exception as e:
        logger.error("failed_to_track_product_unlike",
                     extra={"product_id": instance.product.id, "error": str(e)})


@receiver(product_viewed)
def track_product_view(
    sender: Any,
    request: HttpRequest,
    user_id: int,
    product_id: int,
    product_name: str,
    **kwargs: Any,
) -> None:
    """Track product view event when store emits product_viewed signal and publish it to Kafka."""
    try:
        producer = get_producer()

        # Build user info
        if user_id:
            user_info = RequestParserService.extract_user_info(request, request.user)
        else:
            user_info = {
                'email': None,
                'name': 'Anonymous',
                'ip_address': RequestParserService.get_client_ip(request),
                'user_agent': RequestParserService.get_user_agent(request),
            }

        producer.send_product_viewed(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            user_info=user_info,
        )
        logger.info("product_viewed_signal",
                    extra={"product_id": product_id, "user_id": user_id})
    except Exception as e:
        logger.error("failed_to_track_product_view",
                     extra={"product_id": product_id, "error": str(e)})
