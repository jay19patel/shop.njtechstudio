"""Cart-related event handlers."""
import logging
from typing import Any
from django.dispatch import receiver
from django.http import HttpRequest

from store.signals import cart_item_added
from insights.kafka import get_producer
from insights.services.request_parser import RequestParserService

logger = logging.getLogger(__name__)


@receiver(cart_item_added)
def track_cart_item_added(
    sender: Any,
    request: HttpRequest,
    user_id: int,
    product_id: int,
    product_name: str,
    quantity: int,
    price: float,
    **kwargs: Any,
) -> None:
    """Track cart item added event and publish it to Kafka."""
    try:
        producer = get_producer()
        user_info = RequestParserService.extract_user_info(request, request.user)

        producer.send_cart_item_added(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price,
            user_info=user_info,
        )
        logger.info("cart_item_added_signal",
                    extra={"product_id": product_id, "user_id": user_id, "qty": quantity})
    except Exception as e:
        logger.error("failed_to_track_cart_item_added",
                     extra={"product_id": product_id, "user_id": user_id, "error": str(e)})
