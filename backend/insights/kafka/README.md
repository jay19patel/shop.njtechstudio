# Kafka Event Streaming

This module provides Kafka event producer and consumer utilities for the shop analytics system.

## Structure

- **config.py** — Kafka broker configuration and topic definitions
- **producer.py** — Event producer for publishing events to Kafka
- **consumer.py** — Event consumer/listener for consuming events from Kafka
- **__init__.py** — Public API exports

## Usage

### Publishing Events

Events are published automatically when certain actions occur in the store app (via Django signals):

```python
from insights.kafka import get_producer

producer = get_producer()
producer.send_product_viewed(
    user_id=123,
    product_id=456,
    product_name="Product Name",
    user_info={...}
)
```

### Listening to Events

#### Option 1: Django Management Command (Recommended)

```bash
python manage.py listen_kafka_events
```

With custom consumer group:
```bash
python manage.py listen_kafka_events --group-id my-consumer-group
```

Listen to specific topics only:
```bash
python manage.py listen_kafka_events --topics shop.product.viewed,shop.order.created
```

#### Option 2: Standalone Script

```bash
python kafka_listener.py
```

#### Option 3: In Python Code

```python
from insights.kafka import start_listener

start_listener()
```

Or with custom configuration:

```python
from insights.kafka import KafkaEventListener

listener = KafkaEventListener(
    topics=['shop.product.viewed', 'shop.order.created'],
    group_id='my-consumer-group'
)
listener.run()
```

## Events

The system publishes the following events:

| Event | Topic | Trigger |
|-------|-------|---------|
| Product Viewed | `shop.product.viewed` | User views product details |
| Product Liked | `shop.product.liked` | User likes a product |
| Product Unliked | `shop.product.unliked` | User unlikes a product |
| Cart Item Added | `shop.cart.item_added` | User adds item to cart |
| Cart Item Removed | `shop.cart.item_removed` | User removes item from cart |
| Order Created | `shop.order.created` | User creates an order |

## Event Format

All events follow this structure:

```json
{
  "event_type": "PRODUCT_VIEWED",
  "timestamp": "2026-06-14T10:30:45.123456",
  "user_id": 123,
  "data": {
    "product_id": 456,
    "product_name": "Product Name",
    "user_info": {
      "email": "user@example.com",
      "name": "John Doe",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  }
}
```

## Configuration

Edit `config.py` to change:

- `KAFKA_BROKER` — Kafka broker address (default: `localhost:9092`)
- `KAFKA_TOPICS` — Topic mappings
- `CONSUMER_GROUP_ID` — Consumer group name
- `CONSUMER_AUTO_OFFSET_RESET` — Auto offset reset behavior

## Requirements

- Kafka server running on configured broker
- `kafka-python` package installed

## Architecture

The event system is **fully decoupled**:

1. **Store app** — Emits Django signals when events occur
2. **Insights app** — Listens to signals and publishes to Kafka
3. **Kafka** — Message broker for event streaming
4. **Consumer** — Optional standalone listener for processing events

This design allows the store app to remain independent of Kafka implementation details.
