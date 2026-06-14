"""Kafka event producer for shop events."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from .config import KAFKA_BROKER, KAFKA_TOPICS

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """Produces events to Kafka topics."""

    def __init__(self):
        """Initialize Kafka producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None

    def send_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[int] = None,
        user_info: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send event to Kafka topic.

        Args:
            topic: Kafka topic name
            event_type: Type of event
            data: Event payload
            user_id: User ID (optional)
            user_info: User info dict with email, name, ip_address, user_agent (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.producer:
            logger.warning(f"Kafka producer not available, skipping event: {event_type}")
            return False

        try:
            # Merge user_info into data if provided
            event_data = {**data}
            if user_info:
                event_data['user_info'] = user_info

            event = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'data': event_data,
            }

            future = self.producer.send(topic, value=event)
            record_metadata = future.get(timeout=5)

            logger.info(
                f"Event sent to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"at offset {record_metadata.offset}"
            )
            return True

        except KafkaError as e:
            logger.error(f"Failed to send event to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending event: {e}")
            return False

    def send_product_viewed(
        self, user_id: Optional[int], product_id: int, product_name: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record product view event."""
        return self.send_event(
            KAFKA_TOPICS['product_view'],
            'PRODUCT_VIEWED',
            {'product_id': product_id, 'product_name': product_name},
            user_id=user_id,
            user_info=user_info,
        )

    def send_product_liked(
        self, user_id: int, product_id: int, product_name: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record product like event."""
        return self.send_event(
            KAFKA_TOPICS['product_like'],
            'PRODUCT_LIKED',
            {'product_id': product_id, 'product_name': product_name},
            user_id=user_id,
            user_info=user_info,
        )

    def send_product_unliked(
        self, user_id: int, product_id: int, product_name: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record product unlike event."""
        return self.send_event(
            KAFKA_TOPICS['product_unlike'],
            'PRODUCT_UNLIKED',
            {'product_id': product_id, 'product_name': product_name},
            user_id=user_id,
            user_info=user_info,
        )

    def send_cart_item_added(
        self, user_id: int, product_id: int, product_name: str, quantity: int, price: float,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record cart item added event."""
        return self.send_event(
            KAFKA_TOPICS['cart_item_added'],
            'CART_ITEM_ADDED',
            {
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'price': price,
            },
            user_id=user_id,
            user_info=user_info,
        )

    def send_cart_item_removed(
        self, user_id: int, product_id: int, product_name: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record cart item removed event."""
        return self.send_event(
            KAFKA_TOPICS['cart_item_removed'],
            'CART_ITEM_REMOVED',
            {'product_id': product_id, 'product_name': product_name},
            user_id=user_id,
            user_info=user_info,
        )

    def send_order_created(
        self, user_id: int, order_id: int, total_amount: float, items_count: int,
        user_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record order created event."""
        return self.send_event(
            KAFKA_TOPICS['order_created'],
            'ORDER_CREATED',
            {
                'order_id': order_id,
                'total_amount': total_amount,
                'items_count': items_count,
            },
            user_id=user_id,
            user_info=user_info,
        )

    def close(self):
        """Close Kafka producer."""
        if self.producer:
            self.producer.close()


# Global producer instance
_producer = None


def get_producer() -> KafkaEventProducer:
    """Get or create the global Kafka producer instance."""
    global _producer
    if _producer is None:
        _producer = KafkaEventProducer()
    return _producer
