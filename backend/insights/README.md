# Insights App

Centralized analytics, event tracking, Kafka streaming, and ML/AI features for the shop application.

## Structure

```
insights/
├── __init__.py                  # App initialization
├── apps.py                      # App config with signal registration
├── models.py                    # Analytics models (ProductEmbedding)
├── analytics.py                 # Utility: extract_user_info(), get_client_ip()
├── admin.py                     # Django admin configuration
├── kafka/                       # Kafka event streaming
│   ├── __init__.py             # Exports get_producer()
│   └── producer.py             # KafkaEventProducer class
├── events/                      # Event signal handlers
│   ├── __init__.py             # Event handlers package
│   ├── product_events.py       # Product signals (like, unlike)
│   ├── cart_events.py          # Cart events (placeholder)
│   └── order_events.py         # Order events (placeholder)
├── views.py                     # API views for analytics (future)
├── migrations/                  # Database migrations
└── README.md                    # This file
```

## Features

### Analytics Utilities (`analytics.py`)
- `extract_user_info(request, user)` - Extract user email, name, IP address, user agent
- `get_client_ip(request)` - Get client IP from request
- `get_user_agent(request)` - Get user agent from request

**Usage:**
```python
from insights.analytics import extract_user_info

user_info = extract_user_info(request, request.user)
# Returns: {
#     'email': 'user@example.com',
#     'name': 'John Doe',
#     'ip_address': '192.168.1.1',
#     'user_agent': 'Mozilla/5.0...'
# }
```

### Event Tracking (`events.py`)
Automatic signal handlers for tracking user actions:

#### Product Like/Unlike
- When a user likes a product → Publishes `PRODUCT_LIKED` event to Kafka
- When a user removes like → Publishes `PRODUCT_UNLIKED` event to Kafka
- Includes: user_id, product_id, product_name, user_info

**Signals Used:**
- `post_save` on Like model → Track like event
- `post_delete` on Like model → Track unlike event

## Integration with Other Apps

### Store App
- Imports analytics utilities from insights
- Uses `extract_user_info()` for all user actions

### Kafka Services
- Publishes events to Kafka using functions from `kafka_services`
- Includes user info in all published events

## How It Works

```
Django Request/Signal
    ↓
Event Handler (signals.py)
    ↓
Kafka Service (kafka_services/)
    ↓
Kafka Broker (localhost:9092)
    ↓
Test Listener or External Services
```

## Adding New Event Trackers

1. Create signal handler in `events.py`:
   ```python
   @receiver(post_save, sender=YourModel)
   def track_event(sender, instance, created, **kwargs):
       if created:
           publish_event(
               user_id=instance.user.id,
               data={...},
               user_info={...}
           )
   ```

2. Import Kafka publishing function:
   ```python
   from kafka_services.product_events import publish_product_viewed
   ```

3. Signal will automatically trigger when model is saved/deleted

## Configuration

Add to `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'insights.apps.InsightsConfig',
    'kafka_services',
    ...
]
```

## ProductEmbedding Model

The `ProductEmbedding` model stores vector embeddings for products. Useful for:
- Product recommendations
- Similarity search
- AI/ML features
- Content-based filtering

### Fields

- **product** (OneToOneField) - Reference to Product
- **embedding_name** (CharField) - Name/identifier (e.g., 'product-desc-v1')
- **embedding_version** (CharField) - Version of embedding model
- **embedding_vector** (JSONField) - Vector as JSON array
- **embedding_source** - How it was created (manual, AI, ML, user feedback)
- **description** - Notes about the embedding
- **created_at, updated_at** - Timestamps
- **created_by** - User or system that created it

### Usage

```python
from insights.models import ProductEmbedding
from store.models import Product

# Create or update product embedding
product = Product.objects.get(id=1)
embedding, created = ProductEmbedding.objects.update_or_create(
    product=product,
    defaults={
        'embedding_name': 'product-description-v1',
        'embedding_version': '1.0',
        'embedding_vector': [0.123, 0.456, 0.789, ...],  # Your vector
        'embedding_source': 'ai_generated',
        'description': 'Generated from product description using BERT',
        'created_by': 'ml_pipeline'
    }
)

# Access from product
product.embedding.embedding_vector
```

### Admin Access

Access at `/admin/insights/productembedding/`
- View all product embeddings
- Search by product name or embedding name
- Filter by source and version
- View vector data in collapsible section

## Event Handlers

### Product Events (`events/product_events.py`)

**Signal Handlers:**
- `track_product_like()` - Fires when user likes a product
- `track_product_unlike()` - Fires when user removes like

**Publishes Kafka events:**
- `PRODUCT_LIKED` - User likes product
- `PRODUCT_UNLIKED` - User removes like

## Testing

### View Events in Real-time
```bash
python kafka_services/test_listener.py
```

### Check Signal Registration
```bash
python manage.py shell
from django.core.signals import receiver
from django.db.models.signals import post_save
from store.models import Like
# Should show handlers are registered
```

### Test ProductEmbedding
```bash
python manage.py shell
from insights.models import ProductEmbedding
from store.models import Product

product = Product.objects.first()
embedding = ProductEmbedding.objects.create(
    product=product,
    embedding_name='test-v1',
    embedding_vector=[0.1, 0.2, 0.3]
)
print(embedding)
```

## Future Enhancements

- [ ] Add embedding generation from product descriptions
- [ ] Implement similarity search endpoint
- [ ] Create recommendation engine using embeddings
- [ ] Add support for multiple embedding types
- [ ] Create analytics dashboard
- [ ] Track embedding performance metrics
- [ ] Integrate with external ML services (OpenAI, Hugging Face)
- [ ] Batch embedding generation
- [ ] API endpoints for embedding queries
