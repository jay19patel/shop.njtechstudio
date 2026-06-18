"""Kafka event consumer/listener for shop events."""
import json
import logging
from typing import Any, Dict

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .config import KAFKA_BROKER, ALL_TOPICS, CONSUMER_GROUP_ID, CONSUMER_AUTO_OFFSET_RESET, CONSUMER_MAX_POLL_RECORDS

logger = logging.getLogger(__name__)


class KafkaEventListener:
    """Listens to Kafka events and processes them."""

    def __init__(self, topics=None, group_id=None):
        """
        Initialize Kafka consumer.

        Args:
            topics: List of topics to listen to (defaults to ALL_TOPICS)
            group_id: Consumer group ID (defaults to CONSUMER_GROUP_ID)
        """
        self.topics = topics or ALL_TOPICS
        self.group_id = group_id or CONSUMER_GROUP_ID
        self.consumer = None
        self._init_consumer()

    def _init_consumer(self):
        """Initialize the Kafka consumer."""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=[KAFKA_BROKER],
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset=CONSUMER_AUTO_OFFSET_RESET,
                enable_auto_commit=True,
                max_poll_records=CONSUMER_MAX_POLL_RECORDS,
            )
            logger.info(f"Kafka consumer initialized. Listening to {len(self.topics)} topics")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            self.consumer = None

    def format_event(self, topic: str, message: Dict[str, Any]) -> str:
        """Format event for display."""
        event_type = message.get('event_type', 'UNKNOWN')
        timestamp = message.get('timestamp', 'N/A')
        user_id = message.get('user_id', 'Anonymous')
        data = message.get('data', {})

        # Color codes
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        output = f"\n{BOLD}{BLUE}┌─ Event Received {RESET}\n"
        output += f"{BOLD}Topic:{RESET} {GREEN}{topic}{RESET}\n"
        output += f"{BOLD}Event Type:{RESET} {YELLOW}{event_type}{RESET}\n"
        output += f"{BOLD}User ID:{RESET} {user_id}\n"
        output += f"{BOLD}Timestamp:{RESET} {timestamp}\n"
        output += f"{BOLD}Data:{RESET}\n"

        for key, value in data.items():
            output += f"  • {key}: {value}\n"

        output += f"{BLUE}└{RESET}\n"
        return output

    def process_event(self, topic: str, event: Dict[str, Any]):
        """
        Process an event. Override this method for custom event handling.

        Args:
            topic: Kafka topic name
            event: Event data
        """
        formatted = self.format_event(topic, event)
        print(formatted, flush=True)
        logger.info(f"Event processed from topic {topic}", extra={"event_type": event.get('event_type')})

        # Process user interests scoring based on interaction events
        user_id = event.get('user_id')
        event_type = event.get('event_type')
        data = event.get('data', {})

        if user_id:
            try:
                product_id = data.get('product_id')
                if product_id and event_type in ['PRODUCT_VIEWED', 'PRODUCT_LIKED', 'PRODUCT_UNLIKED', 'CART_ITEM_ADDED']:
                    from insights.services.recommendation import RecommendationService
                    RecommendationService.update_user_profile(user_id=int(user_id), product_id=int(product_id), event_type=event_type)
                elif event_type == 'ORDER_CREATED':
                    order_id = data.get('order_id')
                    if order_id:
                        from store.models import Order
                        from insights.services.recommendation import RecommendationService
                        try:
                            order = Order.objects.prefetch_related('items__product').get(id=order_id)
                            for item in order.items.all():
                                if item.product:
                                    RecommendationService.update_user_profile(user_id=int(user_id), product_id=item.product.id, event_type='ORDER_CREATED')
                        except Order.DoesNotExist:
                            logger.warning(f"Order {order_id} not found in DB to update interests.")
            except Exception as e:
                logger.error(f"Error handling user interests in Kafka listener: {str(e)}")

    def run(self):
        """Start listening to events."""
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return

        try:
            logger.info("Kafka listener started, waiting for events...")
            print("\n🎯 Waiting for events...\n", flush=True)

            for message in self.consumer:
                try:
                    event = message.value
                    self.process_event(message.topic, event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("Listener stopped by user")
            print("\n\n✋ Listener stopped by user", flush=True)
        except Exception as e:
            logger.error(f"Unexpected error in listener: {e}")
        finally:
            self.close()

    def close(self):
        """Close the Kafka consumer."""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")


# Global consumer instance
_consumer = None


def get_consumer(topics=None, group_id=None) -> KafkaEventListener:
    """Get or create the global Kafka consumer instance."""
    global _consumer
    if _consumer is None:
        _consumer = KafkaEventListener(topics=topics, group_id=group_id)
    return _consumer


def start_listener(topics=None, group_id=None):
    """Start the Kafka event listener."""
    listener = get_consumer(topics=topics, group_id=group_id)
    listener.run()
