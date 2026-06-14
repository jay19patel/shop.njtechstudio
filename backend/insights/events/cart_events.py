"""Cart-related event handlers."""
import logging
from django.dispatch import receiver

from store.signals import cart_item_added
from insights.kafka import get_producer
from insights.analytics import extract_user_info

logger = logging.getLogger(__name__)


@receiver(cart_item_added)
def track_cart_item_added(sender, request, user_id, product_id, product_name, quantity, price, **kwargs):
    """Track cart item added event when store emits cart_item_added signal."""
    try:
        producer = get_producer()
        user_info = extract_user_info(request, request.user)

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
