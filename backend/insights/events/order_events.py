"""Order-related event handlers."""
import logging
from django.dispatch import receiver

from store.signals import order_created
from insights.kafka import get_producer
from insights.analytics import extract_user_info

logger = logging.getLogger(__name__)


@receiver(order_created)
def track_order_created(sender, request, user_id, order_id, total_amount, items_count, **kwargs):
    """Track order created event when store emits order_created signal."""
    try:
        producer = get_producer()
        user_info = extract_user_info(request, request.user)

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
