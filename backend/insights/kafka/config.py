"""Kafka configuration constants."""

# Kafka broker address
KAFKA_BROKER = 'localhost:9092'

# Topic definitions
KAFKA_TOPICS = {
    'product_view': 'shop.product.viewed',
    'product_like': 'shop.product.liked',
    'product_unlike': 'shop.product.unliked',
    'cart_item_added': 'shop.cart.item_added',
    'cart_item_removed': 'shop.cart.item_removed',
    'order_created': 'shop.order.created',
}

# All topic names as a list
ALL_TOPICS = list(KAFKA_TOPICS.values())

# Consumer configuration
CONSUMER_GROUP_ID = 'shop-listener-service'
CONSUMER_AUTO_OFFSET_RESET = 'earliest'
CONSUMER_MAX_POLL_RECORDS = 1
