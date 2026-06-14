"""
Service functions for insights - event publishing and tracking.
Store app calls these functions - completely decoupled from Kafka.
"""
import logging
from typing import Any, Dict, Optional

from insights.kafka import get_producer

logger = logging.getLogger(__name__)


def publish_product_view(
    request,
    user_id: Optional[int],
    product_id: int,
    product_name: str,
) -> bool:
    """
    Publish product view event to Kafka.

    Called from: store.views.product.ProductViewSet.retrieve()
    Handles: User info extraction, Kafka publishing
    """
    try:
        from insights.analytics import extract_user_info, get_client_ip

        # Build user info
        if user_id:
            user_info = extract_user_info(request, request.user)
        else:
            user_info = {
                'email': None,
                'name': 'Anonymous',
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }

        # Publish to Kafka
        producer = get_producer()
        result = producer.send_product_viewed(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            user_info=user_info,
        )

        if result:
            logger.info("product_view_published",
                       extra={"product_id": product_id, "user_id": user_id, "ip": user_info.get('ip_address')})
        return result

    except Exception as e:
        logger.error("failed_to_publish_product_view",
                    extra={"product_id": product_id, "error": str(e)})
        return False


def publish_cart_item_added(
    request,
    user_id: int,
    product_id: int,
    product_name: str,
    quantity: int,
    price: float,
) -> bool:
    """
    Publish cart item added event to Kafka.

    Called from: store.views.cart.CartViewSet.add_item()
    Handles: User info extraction, Kafka publishing
    """
    try:
        from insights.analytics import extract_user_info

        user_info = extract_user_info(request, request.user)
        producer = get_producer()
        result = producer.send_cart_item_added(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price,
            user_info=user_info,
        )

        if result:
            logger.info("cart_item_added_published",
                       extra={"product_id": product_id, "user_id": user_id, "qty": quantity})
        return result

    except Exception as e:
        logger.error("failed_to_publish_cart_item_added",
                    extra={"product_id": product_id, "user_id": user_id, "error": str(e)})
        return False


def publish_order_created(
    request,
    user_id: int,
    order_id: int,
    total_amount: float,
    items_count: int,
) -> bool:
    """
    Publish order created event to Kafka.

    Called from: store.views.cart.CartViewSet.checkout()
    Called from: store.views.order.OrderViewSet.create()
    Handles: User info extraction, Kafka publishing
    """
    try:
        from insights.analytics import extract_user_info

        user_info = extract_user_info(request, request.user)
        producer = get_producer()
        result = producer.send_order_created(
            user_id=user_id,
            order_id=order_id,
            total_amount=total_amount,
            items_count=items_count,
            user_info=user_info,
        )

        if result:
            logger.info("order_created_published",
                       extra={"order_id": order_id, "user_id": user_id, "amount": total_amount})
        return result

    except Exception as e:
        logger.error("failed_to_publish_order_created",
                    extra={"order_id": order_id, "user_id": user_id, "error": str(e)})
        return False
