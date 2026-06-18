"""Order-related event handlers."""
import logging
from typing import Any
from django.dispatch import receiver
from django.http import HttpRequest

from store.signals import order_created
from insights.kafka import get_producer
from insights.services.request_parser import RequestParserService

logger = logging.getLogger(__name__)


@receiver(order_created)
def track_order_created(
    sender: Any,
    request: HttpRequest,
    user_id: int,
    order_id: int,
    total_amount: float,
    items_count: int,
    **kwargs: Any,
) -> None:
    """Track order created event and publish it to Kafka."""
    try:
        producer = get_producer()
        user_info = RequestParserService.extract_user_info(request, request.user)

        producer.send_order_created(
            user_id=user_id,
            order_id=order_id,
            total_amount=total_amount,
            items_count=items_count,
            user_info=user_info,
        )
        logger.info("order_created_signal",
                    extra={"order_id": order_id, "user_id": user_id})
    except Exception as e:
        logger.error("failed_to_track_order_created",
                     extra={"order_id": order_id, "error": str(e)})
