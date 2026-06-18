# Insights App — Complete Developer Guide

> **For whom**: This guide is written for both a developer reading code for the first time AND a technical lead who wants to understand every design decision. Every concept is explained from scratch with real code from this project.

---

## Table of Contents

1. [What Does This App Do?](#1-what-does-this-app-do)
2. [System Architecture](#2-system-architecture)
3. [File Structure Map](#3-file-structure-map)
4. [Database Models — Django ORM](#4-database-models--django-orm)
5. [Django Signals — How Auto-Triggers Work](#5-django-signals--how-auto-triggers-work)
6. [Apps.py — How Everything Boots Up](#6-appspy--how-everything-boots-up)
7. [Embedding Service — AI Text to Numbers](#7-embedding-service--ai-text-to-numbers)
8. [Kafka — Event Bus Architecture](#8-kafka--event-bus-architecture)
9. [Event Handlers — What Listens to What](#9-event-handlers--what-listens-to-what)
10. [Recommendation Service — The Brain](#10-recommendation-service--the-brain)
11. [Smart Search — Natural Language Product Search](#11-smart-search--natural-language-product-search)
12. [REST API Views](#12-rest-api-views)
13. [Admin Dashboard — Django Admin Customization](#13-admin-dashboard--django-admin-customization)
14. [Management Commands](#14-management-commands)
15. [End-to-End Flow: User Views a Product](#15-end-to-end-flow-user-views-a-product)
16. [End-to-End Flow: User Searches for Something](#16-end-to-end-flow-user-searches-for-something)
17. [Math Reference — Vectors, Similarity, Decay](#17-math-reference--vectors-similarity-decay)
18. [Django Admin Template — How the HTML Dashboard Works](#18-django-admin-template--how-the-html-dashboard-works)

---

## 1. What Does This App Do?

The `insights` Django app is an **AI-powered analytics engine** that sits alongside the main `store` app. It does three major things:

### A. Tracks User Behaviour in Real-Time
Every time a user **views** a product, **likes** it, **adds it to cart**, or **places an order** — a Kafka event fires. A background daemon listens to these events and builds an AI profile of each user.

### B. Recommends Products & Categories
Using **vector math (cosine similarity)**, it compares each user's interest profile against every product/category embedding in the database and returns the top 5 matches.

### C. Forecasts Stock Demand for Admins
It aggregates interest scores from all users and shows admins **which products are high-demand but low-stock** so they can restock proactively.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER ACTIONS (Frontend)                        │
│   Views Product │ Likes Product │ Adds to Cart │ Places Order           │
└────────────┬────────────────────────────────────────────────────────────┘
             │ HTTP Request hits Django API
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       DJANGO (store app views)                          │
│  store.signals.product_viewed.send(...)  ← Custom Signal emitted       │
│  Like.objects.create(...)               ← ORM triggers post_save signal │
└────────────┬────────────────────────────────────────────────────────────┘
             │ Signal received by insights/events/
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     insights/events/ (Signal Handlers)                  │
│  track_product_view()  → KafkaEventProducer.send_product_viewed()       │
│  track_product_like()  → KafkaEventProducer.send_product_liked()        │
└────────────┬────────────────────────────────────────────────────────────┘
             │ JSON message published to Kafka topic
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Apache Kafka Broker (localhost:9092)                 │
│  Topics:                                                                 │
│    shop.product.viewed  │  shop.product.liked  │  shop.cart.item_added  │
│    shop.order.created   │  shop.product.unliked                         │
└────────────┬────────────────────────────────────────────────────────────┘
             │ KafkaEventListener.run() (background daemon)
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     insights/kafka/consumer.py                           │
│  process_event() → RecommendationService.update_user_profile()          │
└────────────┬────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  RecommendationService (recommendation.py)               │
│  1. Fetch product embedding vector from DB                               │
│  2. Merge with user's existing preference_vector (EMA formula)          │
│  3. Normalize to unit length                                             │
│  4. Save updated UserSemanticProfile to DB                               │
└────────────┬────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Database (PostgreSQL)                             │
│   UserSemanticProfile  │  ProductEmbedding  │  CategoryEmbedding        │
└─────────────────────────────────────────────────────────────────────────┘
             ▲
             │ GET /insights/user-interests/
┌─────────────────────────────────────────────────────────────────────────┐
│                     API Views (REST Framework)                           │
│  UserInterestsView  │  SmartSearchView  │  AdminDemandForecastView       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. File Structure Map

```
backend/insights/
│
├── apps.py                        ← App boot config — registers all signals
├── models.py                      ← 4 database tables defined here
├── admin.py                       ← Django admin panel configuration
├── signals.py                     ← Auto-generate embeddings on Product/Category save
├── serializers.py                 ← DRF serializers for API responses
├── urls.py                        ← URL routes → views mapping
├── tests.py
│
├── services/                      ← All business logic lives here
│   ├── embeddings.py              ← Talks to Ollama AI model
│   ├── recommendation.py          ← Vector math, user profiles, recommendations
│   ├── search.py                  ← Natural language search + LangChain pipeline
│   └── request_parser.py          ← Extracts IP, user-agent from HTTP request
│
├── views/                         ← HTTP endpoints (REST Framework APIViews)
│   ├── search.py                  ← POST /insights/search/
│   ├── user_interests.py          ← GET/DELETE /insights/user-interests/
│   └── admin_demand.py            ← GET /admin/demand-forecast/
│
├── kafka/                         ← Kafka configuration + producer + consumer
│   ├── config.py                  ← Broker address, topic names, consumer settings
│   ├── producer.py                ← Publishes events TO Kafka
│   └── consumer.py                ← Reads events FROM Kafka + calls RecommendationService
│
├── events/                        ← Django signal handlers (bridges store → kafka)
│   ├── product_events.py          ← Handles product view / like / unlike signals
│   ├── cart_events.py             ← Handles cart_item_added signal
│   └── order_events.py            ← Handles order_created signal
│
├── management/commands/
│   ├── generate_embeddings.py     ← CLI: batch-generate all embeddings
│   └── run_kafka_consumer.py      ← CLI: start the Kafka listener daemon
│
└── templates/admin/insights/
    └── demand_forecast.html        ← Custom Django admin HTML dashboard
```

---

## 4. Database Models — Django ORM

> **File**: [models.py](models.py)

Django ORM lets you define database tables as Python classes. Each class = one table. Each field = one column.

### Model 1: `ProductEmbedding`

```python
class ProductEmbedding(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='embedding')
    embedding_name = models.CharField(max_length=255, default="qwen3-embedding")
    embedding_version = models.CharField(max_length=50, default="0.6b")
    embedding_vector = models.JSONField(null=True, blank=True)   # ← 768 floats stored as JSON
    embedding_source = models.CharField(choices=[('ollama', 'Ollama Local'), ('manual', 'Manual')])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**What it stores**: One row per product. The `embedding_vector` column holds a list of 768 float numbers like `[0.012, -0.456, 0.891, ...]`. This is the AI "fingerprint" of a product's text description.

**`OneToOneField`**: A product can only have ONE embedding. If the product is deleted (`CASCADE`), the embedding is automatically deleted too.

**`auto_now_add=True`**: Django automatically fills `created_at` when the row is first created. You never set it manually.

**`auto_now=True`**: Django automatically updates `updated_at` every time `.save()` is called.

**`Meta.ordering = ['-updated_at']`**: All queries return results sorted by newest-updated first, by default.

**`Meta.indexes`**: Two database-level indexes are created so queries on `embedding_source` and `updated_at` are fast.

---

### Model 2: `CategoryEmbedding`

```python
class CategoryEmbedding(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='embedding')
    embedding_vector = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Same concept as `ProductEmbedding` but for categories. Used to find categories semantically similar to a user's preferences.

---

### Model 3: `UserSemanticProfile`

```python
class UserSemanticProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='semantic_profile')
    preference_vector = models.JSONField(null=True, blank=True)    # ← 768 floats: "who this user is"
    category_interests = models.JSONField(default=dict, blank=True) # ← {"3": 7.0, "5": 4.0}
    product_interests = models.JSONField(default=dict, blank=True)  # ← {"42": 12.0, "17": 5.0}
    updated_at = models.DateTimeField(auto_now=True)
```

**What it stores**: One row per user. This is the user's AI profile.

- `preference_vector`: A 768-number vector representing the user's current semantic taste. It's always unit-normalized (magnitude = 1.0). Starts as `null` until first interaction.
- `category_interests`: A plain dict mapping category ID → accumulated score. Example: `{"3": 7.0}` means the user has engaged with category 3 with a total weight of 7.0.
- `product_interests`: Same but for products. `{"42": 12.0}` means product 42 has been viewed once (1.0), liked (3.0), and ordered (10.0) → total 14... wait, scores accumulate.

**`settings.AUTH_USER_MODEL`**: Django best practice — instead of hardcoding `User`, we reference the setting so it works with custom user models.

---

### Model 4: `ProductDemand` (Proxy Model)

```python
class ProductDemand(Product):
    class Meta:
        proxy = True
        verbose_name = "Demand & Stock Forecast"
```

**What is a proxy model?** It's a Python class that points to the same database table as `Product` — no new table is created. Its only purpose is to appear as a separate entry in the Django admin panel so we can attach a custom admin view (the demand forecast dashboard) without polluting the `Product` admin.

---

## 5. Django Signals — How Auto-Triggers Work

> **Files**: [signals.py](signals.py), [events/](events/)

### What are Django Signals?

Django signals are like event listeners. When something happens (e.g., a model is saved), Django fires a signal. Any function that "listens" to that signal gets called automatically.

There are two types used here:

**Type 1 — Built-in ORM Signals** (`post_save`, `post_delete`):
These are signals Django fires automatically when database operations happen.

**Type 2 — Custom Signals** (defined in `store/signals.py`):
The `store` app defines custom signals for analytics: `product_viewed`, `cart_item_added`, `order_created`. These are fired manually by calling `.send()` in view code.

---

### Signal 1: Auto-Generate Product Embedding on Save

> **File**: [signals.py](signals.py) — Line 13

```python
@receiver(post_save, sender=Product)
def generate_product_embedding(sender, instance, created, **kwargs):
    embedding_text = f"{instance.name} {instance.description}"  # Combine name + description
    service = EmbeddingService()
    vector = service.generate_embedding(embedding_text)          # Call Ollama AI
    if vector:
        ProductEmbedding.objects.update_or_create(               # Save to DB
            product=instance,
            defaults={'embedding_vector': vector, 'embedding_source': 'ollama'}
        )
```

**How it works**:
1. Admin creates or edits a product → `Product.save()` is called.
2. Django automatically fires `post_save` signal with the `Product` instance.
3. `generate_product_embedding` runs, sends the product text to Ollama AI.
4. Ollama returns 768 numbers representing the meaning of that text.
5. `update_or_create` either creates a new `ProductEmbedding` or updates the existing one.

**`update_or_create`**: First looks for a `ProductEmbedding` where `product=instance`. If found, updates the `defaults`. If not found, creates a new row with both the lookup field and defaults.

---

### Signal 2: Auto-Generate Category Embedding on Save

> **File**: [signals.py](signals.py) — Line 46

Same as above but fires when a `Category` is saved.

---

### How are Product View / Like / Cart Signals connected?

These are custom signals from the `store` app. The `store` app does not import `insights` (that would create a circular dependency). Instead, `insights` **listens** to `store`'s signals. This is the correct decoupled design.

**Custom signal definition** (`store/signals.py`):
```python
product_viewed = Signal()    # Fired by store views when user loads product detail page
cart_item_added = Signal()   # Fired by cart API when item is added
order_created = Signal()     # Fired by order API when order is placed
```

**Insight app's listener** (`events/product_events.py`):
```python
@receiver(product_viewed)   # ← "I want to listen to product_viewed signal"
def track_product_view(sender, request, user_id, product_id, product_name, **kwargs):
    producer = get_producer()
    user_info = RequestParserService.extract_user_info(request, request.user)
    producer.send_product_viewed(user_id=user_id, product_id=product_id, ...)
```

The `**kwargs` at the end is important — Django passes extra keyword arguments to signal receivers and if you don't have `**kwargs`, the function will raise a `TypeError` if any extra argument is passed.

---

## 6. Apps.py — How Everything Boots Up

> **File**: [apps.py](apps.py)

```python
class InsightsConfig(AppConfig):
    name = "insights"

    def ready(self):
        from insights import events, signals  # noqa
```

**`ready()`** is called by Django exactly once, after all models are loaded, when the app is ready to run. This is where we import the `events` and `signals` modules.

**Why import them here?** The `@receiver` decorators in those files only register themselves when the module is imported. If we never import `events/product_events.py`, none of the Kafka event handlers will ever run. Importing them in `ready()` ensures they're always registered exactly once when Django starts.

**`# noqa`** tells linters (like flake8) to ignore the "imported but unused" warning — we're importing purely for the side effect of registering signal handlers.

---

## 7. Embedding Service — AI Text to Numbers

> **File**: [services/embeddings.py](services/embeddings.py)

### What is an Embedding?

An **embedding** converts text into a list of numbers (a vector) that captures the *meaning* of the text. Texts with similar meaning will have vectors that point in similar directions in 768-dimensional space.

Examples:
- `"Apple iPhone 15 Pro smartphone"` → `[0.12, -0.34, 0.89, ..., 0.02]` (768 numbers)
- `"Samsung Galaxy S24 mobile phone"` → `[0.11, -0.31, 0.87, ..., 0.04]` (similar direction)
- `"Leather sofa living room furniture"` → `[-0.52, 0.71, -0.23, ..., 0.88]` (very different direction)

By comparing these vectors, we can tell that iPhone and Galaxy are semantically similar, while a sofa is completely different.

---

### The `EmbeddingService` class

```python
class EmbeddingService:
    def __init__(self):
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_EMBEDDING_MODEL', 'qwen3-embedding:0.6b')
        self.embeddings = OllamaEmbeddings(base_url=self.base_url, model=self.model)
```

**`getattr(settings, 'KEY', default)`**: Django pattern — read from `settings.py` but use a default if not set. This means the service works even if the developer hasn't added these settings yet.

**`OllamaEmbeddings`**: This comes from the `langchain_community` library. It handles the HTTP call to the locally running Ollama server.

---

### Method: `generate_embedding(text)`

```python
def generate_embedding(self, text: str) -> Optional[List[float]]:
    if not text or not isinstance(text, str):
        return None
    embedding = self.embeddings.embed_query(text.strip())
    return embedding  # List of 768 floats
```

**Usage example**:
```python
service = EmbeddingService()
vector = service.generate_embedding("Sony WH-1000XM5 noise cancelling headphones")
# vector = [0.034, -0.127, 0.891, ...]  → 768 numbers
```

---

### Method: `batch_generate_embeddings(texts)`

```python
def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
    embeddings = self.embeddings.embed_documents(texts)
    return embeddings
```

Sends multiple texts to Ollama in one call. Used by the `generate_embeddings` management command. `embed_documents` is more efficient than calling `embed_query` in a loop.

---

### Method: `calculate_similarity(embedding1, embedding2)`

```python
@staticmethod
def calculate_similarity(embedding1, embedding2) -> float:
    vec1 = np.array(embedding1).reshape(1, -1)
    vec2 = np.array(embedding2).reshape(1, -1)
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return float(similarity)
```

Uses scikit-learn's `cosine_similarity`. Returns a float from -1.0 (opposite meaning) to 1.0 (identical meaning). Used in `SmartSearch.search()` to score how relevant each product is to the search query.

---

## 8. Kafka — Event Bus Architecture

> **Files**: [kafka/config.py](kafka/config.py), [kafka/producer.py](kafka/producer.py), [kafka/consumer.py](kafka/consumer.py)

### What is Kafka and Why Use It?

Kafka is a **message queue / event bus**. When a user views a product, we need to update their AI profile. But doing that synchronously (during the HTTP request) would be slow — it involves DB queries, vector math, another DB write. The user would see lag.

Kafka decouples this:
1. HTTP request: just publish a small JSON message to Kafka (takes ~5ms). Request returns fast.
2. Background daemon: reads from Kafka and does the heavy processing (can take 100ms+) without blocking the user.

---

### Configuration

> **File**: [kafka/config.py](kafka/config.py)

```python
KAFKA_BROKER = 'localhost:9092'

KAFKA_TOPICS = {
    'product_view':    'shop.product.viewed',
    'product_like':    'shop.product.liked',
    'product_unlike':  'shop.product.unliked',
    'cart_item_added': 'shop.cart.item_added',
    'cart_item_removed': 'shop.cart.item_removed',
    'order_created':   'shop.order.created',
}

ALL_TOPICS = list(KAFKA_TOPICS.values())   # Consumer subscribes to all of these

CONSUMER_GROUP_ID = 'shop-listener-service'
CONSUMER_AUTO_OFFSET_RESET = 'earliest'
CONSUMER_MAX_POLL_RECORDS = 1
```

**`CONSUMER_GROUP_ID`**: Kafka uses consumer groups to ensure each message is processed by exactly one consumer in the group. If you run multiple consumer instances, Kafka distributes messages between them. Since we always use the same group ID, scaling is automatic.

**`CONSUMER_AUTO_OFFSET_RESET = 'earliest'`**: If the consumer starts fresh (no previous offset stored), read all messages from the beginning of the topic. This ensures no events are missed.

**`CONSUMER_MAX_POLL_RECORDS = 1`**: Process one message at a time. Keeps things simple and predictable.

---

### The Producer — Publishing Events

> **File**: [kafka/producer.py](kafka/producer.py)

**Singleton Pattern**: The module-level `_producer` variable ensures only one `KafkaProducer` instance exists per process. Creating a Kafka connection is expensive, so we reuse it.

```python
_producer = None

def get_producer() -> KafkaEventProducer:
    global _producer
    if _producer is None:
        _producer = KafkaEventProducer()   # Created only once
    return _producer
```

**Producer initialization**:
```python
self.producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Dict → JSON bytes
    acks='all',    # Wait for all Kafka replicas to acknowledge before confirming
    retries=3,     # Retry up to 3 times on failure
)
```

**`acks='all'`**: The producer waits until all Kafka broker replicas have written the message before returning success. This means no messages are lost even if a broker crashes immediately after receiving a message.

---

### The Generic `send_event` method

```python
def send_event(self, topic, event_type, data, user_id=None, user_info=None):
    event = {
        'event_type': event_type,               # e.g., "PRODUCT_VIEWED"
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'data': {**data, 'user_info': user_info}
    }
    future = self.producer.send(topic, value=event)  # Non-blocking publish
    record_metadata = future.get(timeout=5)          # Wait max 5s for confirmation
```

**`future.get(timeout=5)`**: The `send` call is non-blocking (returns immediately). The `.get()` call blocks until Kafka confirms receipt or 5 seconds pass (raises exception on timeout). This gives us reliability without waiting indefinitely.

**What the final Kafka message looks like**:
```json
{
    "event_type": "PRODUCT_VIEWED",
    "timestamp": "2026-06-19T10:30:45.123456",
    "user_id": 42,
    "data": {
        "product_id": 17,
        "product_name": "Sony WH-1000XM5",
        "user_info": {
            "email": "user@example.com",
            "name": "Jay",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Macintosh...)"
        }
    }
}
```

---

### Convenience methods on the producer

```python
producer.send_product_viewed(user_id=42, product_id=17, product_name="Sony...")
producer.send_product_liked(user_id=42, product_id=17, product_name="Sony...")
producer.send_cart_item_added(user_id=42, product_id=17, product_name="Sony...", quantity=2, price=24999.0)
producer.send_order_created(user_id=42, order_id=99, total_amount=49998.0, items_count=2)
```

Each of these just calls `send_event` with the correct topic and event_type. They make call sites readable.

---

### The Consumer — Reading Events

> **File**: [kafka/consumer.py](kafka/consumer.py)

```python
self.consumer = KafkaConsumer(
    *self.topics,                                      # Subscribe to all topics
    bootstrap_servers=[KAFKA_BROKER],
    group_id=self.group_id,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # JSON bytes → dict
    auto_offset_reset=CONSUMER_AUTO_OFFSET_RESET,
    enable_auto_commit=True,                           # Automatically mark messages as read
    max_poll_records=CONSUMER_MAX_POLL_RECORDS,
)
```

**`enable_auto_commit=True`**: After processing a message, Kafka automatically stores the "offset" (current position). If the consumer restarts, it picks up from where it left off.

---

### The `run()` loop

```python
def run(self):
    for message in self.consumer:             # Blocks waiting for new messages
        event = message.value                 # Already deserialized to dict
        self.process_event(message.topic, event)
```

This is a **blocking infinite loop**. It sits and waits. When a new message arrives on any subscribed topic, `process_event` is called.

---

### The `process_event()` method — where it all connects

```python
def process_event(self, topic, event):
    user_id = event.get('user_id')
    event_type = event.get('event_type')
    data = event.get('data', {})

    if user_id:
        product_id = data.get('product_id')
        
        if product_id and event_type in ['PRODUCT_VIEWED', 'PRODUCT_LIKED', 'PRODUCT_UNLIKED', 'CART_ITEM_ADDED']:
            RecommendationService.update_user_profile(
                user_id=int(user_id), product_id=int(product_id), event_type=event_type
            )
        
        elif event_type == 'ORDER_CREATED':
            order = Order.objects.prefetch_related('items__product').get(id=order_id)
            for item in order.items.all():
                RecommendationService.update_user_profile(
                    user_id=int(user_id), product_id=item.product.id, event_type='ORDER_CREATED'
                )
```

**Why `ORDER_CREATED` is special**: An order can contain multiple products. The consumer fetches the entire order and calls `update_user_profile` once per item — so each item in the order contributes to the user's AI profile.

**`prefetch_related('items__product')`**: Django optimization. Without this, accessing `order.items.all()` causes N+1 queries (one query per item). `prefetch_related` fetches all items and their products in 2 extra SQL queries, not N.

---

## 9. Event Handlers — What Listens to What

> **File**: [events/](events/)

These are the bridge between Django's signal system and Kafka.

### Product Like Handler

```python
@receiver(post_save, sender=Like)
def track_product_like(sender, instance, created, **kwargs):
    if created:                              # ← Only on NEW likes, not on edits
        producer = get_producer()
        producer.send_product_liked(
            user_id=instance.user.id,
            product_id=instance.product.id,
            product_name=instance.product.name,
        )
```

**`if created`**: The `post_save` signal fires both when a row is created AND when it's updated. We check `created` to only track when the like is first added, not if it's somehow re-saved.

### Product Unlike Handler

```python
@receiver(post_delete, sender=Like)
def track_product_unlike(sender, instance, **kwargs):
    producer = get_producer()
    producer.send_product_unliked(...)      # ← No `created` check, delete always means unlike
```

`post_delete` fires after the `Like` row is deleted from the database.

### Product View Handler

```python
@receiver(product_viewed)   # ← Custom signal from store app
def track_product_view(sender, request, user_id, product_id, product_name, **kwargs):
    if user_id:
        user_info = RequestParserService.extract_user_info(request, request.user)
    else:
        user_info = {
            'email': None, 'name': 'Anonymous',
            'ip_address': RequestParserService.get_client_ip(request),
            'user_agent': RequestParserService.get_user_agent(request),
        }
    producer.send_product_viewed(user_id=user_id, ...)
```

Anonymous users (not logged in) can still view products. The handler gracefully handles this by sending `user_id=None`. The consumer will skip profile update for anonymous users because `if user_id:` is `False` for `None`.

---

### RequestParserService

> **File**: [services/request_parser.py](services/request_parser.py)

```python
@staticmethod
def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()   # First IP in chain is the real client
    return request.META.get('REMOTE_ADDR', '')

@staticmethod
def extract_user_info(request, user) -> dict:
    return {
        'email': user.email,
        'name': user.first_name or user.username,
        'ip_address': RequestParserService.get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
    }
```

**`HTTP_X_FORWARDED_FOR`**: When requests go through a proxy or load balancer (like Nginx), the real client IP is in this header as a comma-separated list. The first IP is the original client.

**`REMOTE_ADDR`**: The direct connection IP. If there's no proxy, this is the real client IP.

---

## 10. Recommendation Service — The Brain

> **File**: [services/recommendation.py](services/recommendation.py)

This is the most important file in the app. It does all the vector math.

### Event Weight Constants

```python
EVENT_WEIGHTS = {
    'PRODUCT_VIEWED':  1.0,    # Weakest signal — just curiosity
    'PRODUCT_LIKED':   3.0,    # Moderate signal — clear positive interest
    'PRODUCT_UNLIKED': -3.0,   # Negative signal — actively disliked
    'CART_ITEM_ADDED': 5.0,    # Strong signal — purchase intent
    'ORDER_CREATED':   10.0,   # Strongest signal — actual purchase
}

DECAY_RATE = 0.25   # How much the new event influences the profile (25%)
```

**Design reasoning**: An order is 10x more significant than a view. This weight system ensures a user's profile is dominated by what they actually buy, not just what they casually browse.

---

### Method: `_normalize_vector(vector)`

```python
@staticmethod
def _normalize_vector(vector: List[float]) -> List[float]:
    magnitude = math.sqrt(sum(x * x for x in vector))   # L2 norm = √(x₁² + x₂² + ... + xₙ²)
    if magnitude == 0:
        return vector
    return [x / magnitude for x in vector]               # Each element ÷ magnitude
```

**Why normalize?** When we use dot product for similarity, if vectors have different magnitudes, the dot product is affected by the magnitude, not just the direction. By normalizing to unit length (magnitude = 1.0), dot product becomes equivalent to cosine similarity, which only measures directional alignment.

**Example**:
```
vector = [3.0, 4.0]
magnitude = √(9 + 16) = √25 = 5.0
normalized = [3/5, 4/5] = [0.6, 0.8]
# Magnitude of normalized = √(0.36 + 0.64) = √1.0 = 1.0 ✓
```

---

### Method: `_dot_product(v1, v2)`

```python
@staticmethod
def _dot_product(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2):
        return 0.0
    return sum(x * y for x, y in zip(v1, v2))
```

**Example** (simplified to 3 dimensions):
```
v1 = [0.6, 0.0, 0.8]   (user profile vector)
v2 = [0.5, 0.1, 0.9]   (product embedding)
dot = (0.6×0.5) + (0.0×0.1) + (0.8×0.9) = 0.3 + 0.0 + 0.72 = 1.02
```

Since both are unit vectors, this score represents cosine similarity. Higher = more similar.

---

### Method: `update_user_profile(user_id, product_id, event_type)`

This is the core update function called by the Kafka consumer.

```python
@classmethod
def update_user_profile(cls, user_id: int, product_id: int, event_type: str) -> None:
    weight = EVENT_WEIGHTS.get(event_type)
    if weight is None:
        return   # Unknown event type, skip

    # Step 1: Fetch product and its category
    product = Product.objects.select_related('category').get(id=product_id)
    category = product.category

    # Step 2: Get the product's AI vector
    prod_emb = ProductEmbedding.objects.filter(product=product).first()
    product_vector = prod_emb.embedding_vector if prod_emb else None

    # Step 3: Get or create the user's profile
    profile, created = UserSemanticProfile.objects.get_or_create(
        user_id=user_id,
        defaults={'preference_vector': None, 'category_interests': {}, 'product_interests': {}}
    )

    # Step 4: Update raw interest scores
    cat_interests[str(category.id)] = max(0.0, old_score + weight)   # Can't go below 0
    prod_interests[str(product.id)] = max(0.0, old_score + weight)

    # Step 5: Merge product vector into user preference vector
    if product_vector:
        user_vector = profile.preference_vector
        if not user_vector:
            # First time: just copy and normalize the product vector
            profile.preference_vector = cls._normalize_vector(product_vector)
        else:
            # Subsequent times: Exponential Moving Average merge
            merged = [
                (1.0 - DECAY_RATE) * old_val + DECAY_RATE * weight * prod_val
                for old_val, prod_val in zip(user_vector, product_vector)
            ]
            profile.preference_vector = cls._normalize_vector(merged)

    profile.save()
```

**`get_or_create`**: Atomically checks if a row exists; if not, creates it. Returns `(instance, created_bool)`. This avoids race conditions.

**`max(0.0, old_score + weight)`**: Unlike interest scores, we never let them go negative. If a user likes then unlikes, scores return to 0, not below.

**EMA Formula**:
```
new_value[i] = (1 - λ) × old_value[i]  +  λ × weight × product_value[i]
             = 0.75 × old_value[i]      +  0.25 × weight × product_value[i]
```

With `DECAY_RATE = 0.25`, old data has 75% influence and new events have 25% influence × their weight. An ORDER_CREATED (weight=10) effectively pulls the user vector very strongly toward that product.

**Concrete example**:
```
User's current vector dimension[0] = 0.6
Product's vector dimension[0] = 0.9
Event: CART_ITEM_ADDED (weight = 5.0)

merged[0] = (1 - 0.25) × 0.6 + 0.25 × 5.0 × 0.9
           = 0.75 × 0.6 + 1.25 × 0.9
           = 0.45 + 1.125
           = 1.575
```

Then the whole merged vector is normalized to unit length.

---

### Method: `get_top_categories(user_id, limit=5)`

```python
@classmethod
def get_top_categories(cls, user_id: int, limit: int = 5) -> List[Dict]:
    profile = UserSemanticProfile.objects.filter(user_id=user_id).first()
    user_vector = profile.preference_vector

    active_embeddings = CategoryEmbedding.objects.filter(
        embedding_vector__isnull=False
    ).select_related('category')

    scores = []
    for emb in active_embeddings:
        sim = cls._dot_product(user_vector, emb.embedding_vector)   # Cosine similarity
        scores.append((emb.category, sim))

    scores.sort(key=lambda x: x[1], reverse=True)   # Highest similarity first
    return [
        {"category_id": item[0].id, "name": item[0].name, "score": round(item[1], 4)}
        for item in scores[:limit]
    ]
```

**`embedding_vector__isnull=False`**: Django ORM filter syntax. `__isnull=False` means only rows where the column is NOT NULL. This avoids categories that failed to get an embedding.

**`select_related('category')`**: SQL JOIN optimization. Without this, accessing `emb.category` for each embedding would fire a separate SQL query. `select_related` fetches all categories in one JOIN.

---

### Method: `get_user_interests_data(user_id)`

```python
# 1. Try semantic matching first (primary path)
if profile.preference_vector:
    top_cats = cls.get_top_categories(user_id=user_id, limit=5)
    top_prods = cls.get_top_products(user_id=user_id, limit=5)
    if top_cats or top_prods:
        return {"top_categories": top_cats, "top_products": top_prods}

# 2. Fallback: use raw interaction counts (for new users with no vector yet)
cat_scores = profile.category_interests or {}
sorted_cat_ids = sorted(cat_scores.keys(), key=lambda k: cat_scores[k], reverse=True)[:5]
categories = {str(c.id): c.name for c in Category.objects.filter(id__in=...)}
```

**Why the fallback?** A brand new user who interacted before the Ollama service was running won't have a `preference_vector` (because embedding generation failed). The fallback uses raw scores so they still get some recommendations.

---

### Method: `reset_user_profile(user_id)`

```python
profile.preference_vector = None
profile.category_interests = {}
profile.product_interests = {}
profile.save()
```

Called when user hits `DELETE /insights/user-interests/`. Completely wipes their AI profile. The next interaction will start fresh.

---

## 11. Smart Search — Natural Language Product Search

> **File**: [services/search.py](services/search.py)

### What It Does

Instead of matching keywords, Smart Search understands the *meaning* of a query. It also parses filters from natural language.

Examples:
- `"laptops under 50000"` → finds laptops, applies price_max=50000
- `"cheapest bluetooth headphones in stock"` → finds headphones, sorts by price ascending, only in-stock
- `"sabse sasta phone"` → Hindi phrase detected, sorts by price ascending, finds phones

---

### LangChain LCEL Pipeline

The search uses **LangChain LCEL** (LangChain Expression Language) to chain 4 processing nodes sequentially:

```python
_intent_chain = (
    RunnablePassthrough()          # Pass input state dict through unchanged
    | RunnableLambda(_node_price)   # Step 1: Extract price constraints
    | RunnableLambda(_node_category)# Step 2: Detect category
    | RunnableLambda(_node_stock)   # Step 3: Check stock preference
    | RunnableLambda(_node_sort)    # Step 4: Detect sort preference
)
```

**What is LCEL?** The `|` operator chains callables together. The output of each function becomes the input of the next. It's like a Unix pipe for Python functions. Each node receives the state dict, adds data to it, and returns the modified dict.

**Initial state**:
```python
{
    "query": "laptops under 50000",
    "price_min": None,
    "price_max": None,
    "category_id": None,
    "category_name": None,
    "only_in_stock": False,
    "sort_by": "relevance",
}
```

---

### Node 1: `_node_price` — Price Extraction

```python
def _node_price(state: Dict) -> Dict:
    q = state["query"].lower()
    q = re.sub(r'₹|rs\.?|inr', '', q)    # Remove currency symbols

    # Range: "between 100 and 500" or "from 100 to 500"
    range_pat = r'(?:in\s*be+twe+en|between|from)\s*(\d+(?:\.\d+)?)\s*(?:to|and|-)\s*(\d+(?:\.\d+)?)'
    m = re.search(range_pat, q)
    if m:
        state["price_min"] = float(m.group(1))
        state["price_max"] = float(m.group(2))
        return state

    # Less than / max: "under 50000", "less then 30000" (typo tolerated)
    max_pat = r'(?:less\s+th[ae]n|under|below|cheaper\s+th[ae]n|<)\s*(\d+(?:\.\d+)?)'
    m = re.search(max_pat, q)
    if m:
        state["price_max"] = float(m.group(1))
        return state

    # Greater than / min: "above 10000", "more than 5000"
    min_pat = r'(?:more\s+th[ae]n|above|greater\s+th[ae]n|over|>)\s*(\d+(?:\.\d+)?)'
    m = re.search(min_pat, q)
    if m:
        state["price_min"] = float(m.group(1))
        return state
```

**`re.search(pattern, string)`**: Searches for the pattern anywhere in the string. `re.match` only checks the beginning.

**`(?:...)` vs `(...)`**: `(?:...)` is a non-capturing group (groups for matching only). `(...)` is a capturing group (saves the matched text for `.group(1)`, `.group(2)`, etc.).

**`th[ae]n`**: Matches both "than" and "then" — tolerates the common typo.

---

### Node 2: `_node_category` — Category Detection

```python
def _node_category(state: Dict) -> Dict:
    q = state["query"].lower()

    # Try actual DB category names first
    for cat in Category.objects.values("id", "name"):
        if cat["name"].lower() in q or q in cat["name"].lower():
            state["category_id"] = cat["id"]     # Exact DB match
            return state

    # Keyword fallback
    keywords = {
        "laptop": ["laptop", "notebooks"],
        "phone": ["phone", "mobile", "smartphone"],
        "headphone": ["headphone", "earphone", "earbuds", "headset"],
        ...
    }
    for cat_name, terms in keywords.items():
        if any(t in q for t in terms):
            state["category_name"] = cat_name    # Soft match (no DB ID)
            break
```

**Why DB first?** If an admin creates a category called "Gaming Laptops", it will match the query "gaming laptops" exactly. The hardcoded keywords are just a safety net for common terms.

**`Category.objects.values("id", "name")`**: Returns a QuerySet of dicts (not model instances). More efficient because Django skips creating full model objects.

---

### Node 3 & 4: Stock and Sort

```python
def _node_stock(state):
    state["only_in_stock"] = any(kw in q for kw in
        ["in stock", "available", "stock mein", "available hai", "stocked"])
    return state

def _node_sort(state):
    if any(w in q for w in ["cheapest", "lowest price", "budget", "sabse sasta", "affordable"]):
        state["sort_by"] = "price_asc"
    elif any(w in q for w in ["expensive", "premium", "highest", "best quality"]):
        state["sort_by"] = "price_desc"
    else:
        state["sort_by"] = "relevance"
    return state
```

---

### The Main `search()` Method

```python
def search(self, query: str, limit: int = 16) -> Dict:
    # Step 1: Parse intent
    intent = parse_intent(query)

    # Step 2: Generate embedding for the search query itself
    query_embedding = self.service.generate_embedding(query)

    # Step 3: Fetch all product embeddings (active products only)
    qs = ProductEmbedding.objects.filter(
        embedding_vector__isnull=False,
        product__is_active=True,
    ).select_related("product__category")

    # Step 4: Set semantic threshold
    # Lower threshold (0.2) when explicit filters exist — be permissive
    # Higher threshold (0.4) for free-form — be stricter about relevance
    semantic_threshold = 0.2 if (has_price_filter or has_category_filter) else 0.4

    results = []
    for emb in qs:
        p = emb.product

        # Hard filters (exact match required)
        if intent["price_max"] and float(p.base_price) > intent["price_max"]: continue
        if intent["price_min"] and float(p.base_price) < intent["price_min"]: continue
        if intent["category_id"] and p.category_id != intent["category_id"]: continue
        if intent["only_in_stock"] and p.available_quantity < 1: continue

        # Semantic score
        score = self.service.calculate_similarity(query_embedding, emb.embedding_vector)
        if score < semantic_threshold: continue

        results.append({**self._fmt(p), "similarity_score": round(score, 3)})

    # Step 5: Sort results
    if intent["sort_by"] == "price_asc":
        results.sort(key=lambda x: x["base_price"])
    elif intent["sort_by"] == "price_desc":
        results.sort(key=lambda x: x["base_price"], reverse=True)
    else:
        results.sort(key=lambda x: x["similarity_score"], reverse=True)  # Best match first

    return {"results": results[:limit], "total_results": len(results), ...}
```

**`product__is_active=True`**: Django ORM allows you to filter across related models using `__`. This translates to a SQL JOIN: `WHERE product.is_active = TRUE`.

**`select_related("product__category")`**: Fetches product AND category in one query. Without this, accessing `emb.product.category.name` would be 3 separate queries per embedding.

---

### The `_fmt()` static method

```python
@staticmethod
def _fmt(p) -> Dict:
    img = ProductImage.objects.filter(
        product=p, is_primary=True
    ).values_list("image_url", flat=True).first()

    return {
        "product_id": p.id,
        "product_name": p.name,
        "slug": p.slug,
        "description": (p.description[:90] + "…") if len(p.description) > 90 else p.description,
        "base_price": float(p.base_price),
        "discount_percentage": float(p.discount_percentage),
        "available_quantity": p.available_quantity,
        "category": p.category.name,
        "image": img,
    }
```

**`values_list("image_url", flat=True).first()`**: Returns just the `image_url` string (not a full model object). `flat=True` means instead of `[("url",)]` we get `["url"]`. `.first()` returns the first value or `None`.

**Description truncation**: `p.description[:90] + "…"` limits description to 90 characters for API response efficiency.

---

## 12. REST API Views

> **Files**: [views/](views/)

All views use Django REST Framework's `APIView` class.

### View 1: SmartSearchView

```
POST /insights/search/
Body: {"query": "laptops under 50000", "limit": 16}
Authentication: Not required (public search)
```

```python
class SmartSearchView(APIView):
    def post(self, request):
        query = request.data.get('query', '').strip()
        limit = int(request.data.get('limit', 16))
        result = SmartSearch().search(query=query, limit=limit)
        return Response(result)
```

**`request.data`**: DRF parses request body (JSON, form data, etc.) automatically. Equivalent to `request.POST` but also handles JSON bodies.

**Example response**:
```json
{
    "message": "Found 3 products under ₹50000!",
    "results": [
        {
            "product_id": 17,
            "product_name": "Dell Inspiron 15",
            "slug": "dell-inspiron-15",
            "description": "Dell Inspiron 15 laptop with Intel Core i5...",
            "base_price": 45999.0,
            "discount_percentage": 5.0,
            "available_quantity": 8,
            "category": "Laptops",
            "image": "https://...",
            "similarity_score": 0.847
        }
    ],
    "total_results": 3,
    "filters_applied": {"price_max": 50000, "sort_by": "relevance"},
    "query": "laptops under 50000"
}
```

---

### View 2: UserInterestsView

```
GET /insights/user-interests/
Authentication: Required (JWT token)
```

```python
class UserInterestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = RecommendationService.get_user_interests_data(user_id=request.user.id)
        return Response(data)

    def delete(self, request):
        RecommendationService.reset_user_profile(user_id=request.user.id)
        return Response({"success": "User interest profile cleared"})
```

**`permission_classes = [permissions.IsAuthenticated]`**: DRF automatically rejects requests without valid authentication. Returns HTTP 401 if not logged in.

**`request.user.id`**: DRF populates `request.user` from the JWT token in the `Authorization` header.

**Example GET response**:
```json
{
    "top_categories": [
        {"category_id": 3, "name": "Laptops", "score": 0.9245},
        {"category_id": 7, "name": "Accessories", "score": 0.8102}
    ],
    "top_products": [
        {"product_id": 42, "name": "MacBook Air M3", "score": 0.9671},
        {"product_id": 17, "name": "Dell XPS 15", "score": 0.9134}
    ]
}
```

---

### View 3: AdminDemandForecastView

```
GET /admin/demand-forecast/
Authentication: Required (Admin/Superuser only)
```

```python
class AdminDemandForecastView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        profiles = UserSemanticProfile.objects.all()

        product_scores = defaultdict(float)   # Auto-initializes missing keys to 0.0
        for profile in profiles:
            for pid, score in (profile.product_interests or {}).items():
                product_scores[int(pid)] += float(score)   # Accumulate across all users
```

**`defaultdict(float)`**: A Python dict that returns `0.0` for missing keys instead of raising `KeyError`. Perfect for accumulation.

**Example response**:
```json
{
    "product_demand": [
        {
            "product_id": 42,
            "name": "MacBook Air M3",
            "category_name": "Laptops",
            "score": 87.5,
            "stock": 3,
            "stock_status": "CRITICAL LOW",
            "status_color": "orange",
            "action": "Restock Immediately"
        }
    ],
    "category_demand": [
        {"category_id": 3, "name": "Laptops", "score": 245.0}
    ]
}
```

---

## 13. Admin Dashboard — Django Admin Customization

> **Files**: [admin.py](admin.py), [templates/admin/insights/demand_forecast.html](templates/admin/insights/demand_forecast.html)

### Standard Admin Registrations

```python
@admin.register(ProductEmbedding)
class ProductEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('product', 'embedding_name', 'embedding_version', 'embedding_source', 'updated_at')
    search_fields = ('product__name', 'embedding_name', 'description')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Vector Data', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',)    # ← Collapsed by default (huge JSON field)
        }),
        ...
    )
```

**`search_fields = ('product__name',)`**: Enables the search box in the list view. `product__name` means it searches the related Product model's `name` field. Django generates: `WHERE product.name ILIKE '%query%'`.

**`fieldsets`**: Groups fields into sections in the detail/edit view. `'classes': ('collapse',)` adds a "Show/Hide" toggle for that section — useful for `embedding_vector` which is a huge JSON array.

**`ordering = ('-updated_at',)`**: Default ordering for the list view. The `-` means descending (newest first).

---

### Custom Admin View — ProductDemandAdmin

This is where Django admin customization gets interesting:

```python
@admin.register(ProductDemand)
class ProductDemandAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Override the default list view entirely
        from django.shortcuts import render

        # 1. Aggregate all user profiles
        profiles = UserSemanticProfile.objects.all()
        product_scores = defaultdict(float)
        for profile in profiles:
            for pid, score in (profile.product_interests or {}).items():
                product_scores[int(pid)] += float(score)

        # 2. Build demand report
        product_demand = []
        for pid, score in product_scores.items():
            if pid in products:
                prod = products[pid]
                stock_status = "OUT OF STOCK" if stock == 0 else "CRITICAL LOW" if stock < 5 else ...
                action = "Restock Immediately" if stock < 10 and score >= 5.0 else "Monitor"
                product_demand.append({...})

        product_demand.sort(key=lambda x: x["score"], reverse=True)

        # 3. Render custom template
        context = {
            "title": "Demand & Stock Forecast",
            "product_demand": product_demand,
            "category_demand": category_demand,
            "opts": self.model._meta,    # Required by Django admin base template
        }
        return render(request, "admin/insights/demand_forecast.html", context)
```

**`changelist_view`**: This is Django admin's method for the "list all objects" page (the default table view). By overriding it, we replace the standard table with our custom HTML template. The method signature must match Django's expected signature.

**`self.model._meta`**: Contains metadata about the model (app_label, verbose_name, etc.). Required by Django admin's base template (`admin/base_site.html`) for breadcrumbs and page title.

---

### The Admin HTML Template

> **File**: [templates/admin/insights/demand_forecast.html](templates/admin/insights/demand_forecast.html)

```django
{% extends "admin/base_site.html" %}   {# Inherit Django admin's nav bar, CSS #}
{% load i18n static %}                  {# Load Django template tag libraries #}

{% block extrastyle %}
{{ block.super }}                       {# Keep parent's CSS #}
<style>
    /* Custom CSS for the dashboard */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 2.2fr 1fr;   {# 2 columns: products (wider) + categories #}
    }
    .badge-red { background-color: #fef2f2; color: #dc2626; }    {# OUT OF STOCK #}
    .badge-orange { background-color: #fff7ed; color: #ea580c; } {# CRITICAL LOW #}
    .badge-yellow { ... }  {# LOW STOCK #}
    .badge-green { ... }   {# IN STOCK #}
</style>
{% endblock %}

{% block content %}
<table class="demand-table">
    {% for item in product_demand %}     {# Loop over Python context variable #}
    <tr>
        <td>{{ item.product.name }}</td>
        <td>
            <span class="badge badge-{{ item.status_color }}">{{ item.stock_status }}</span>
        </td>
        <td>
            {% if item.action == "Restock Immediately" %}
            <a href="/admin/store/product/{{ item.product.id }}/change/" 
               class="btn-action" style="background-color: #dc2626;">Restock</a>
            {% else %}
            <a href="..." class="btn-action">Edit Stock</a>
            {% endif %}
        </td>
    </tr>
    {% empty %}                          {# Shown when product_demand list is empty #}
    <tr>
        <td colspan="6">No data yet. Browse products to populate this radar.</td>
    </tr>
    {% endfor %}
</table>
{% endblock %}
```

**`{% extends "admin/base_site.html" %}`**: This template inherits from Django's built-in admin base. We get the navigation bar, breadcrumbs, and login state for free.

**`{% block content %}`**: We override only the content area. Everything else (header, nav, footer) comes from the parent.

**`{{ item.status_color }}`**: `status_color` is a Python string like `"red"` or `"orange"`. Django template renders it inline, producing `class="badge badge-red"`. This is how Python data drives CSS classes.

**`{% if item.action == "Restock Immediately" %}`**: Django template conditionals. Shows a red "Restock" button vs a standard "Edit Stock" button based on the action string.

**`{% empty %}`**: Inside a `{% for %}` tag, `{% empty %}` is rendered when the loop has zero items. This is Django's built-in alternative to `if list: ... else: ...`.

**"Restock" link**: `href="/admin/store/product/{{ item.product.id }}/change/"` — clicking "Restock" takes the admin directly to that product's edit page where they can update `available_quantity`.

---

## 14. Management Commands

### Command 1: `generate_embeddings`

```bash
python manage.py generate_embeddings
python manage.py generate_embeddings --only-missing
```

> **File**: [management/commands/generate_embeddings.py](management/commands/generate_embeddings.py)

```python
class Command(BaseCommand):
    help = 'Generate or update embeddings for all existing products and categories'

    def add_arguments(self, parser):
        parser.add_argument('--only-missing', action='store_true', ...)

    def handle(self, *args, **options):
        only_missing = options['only_missing']
        service = EmbeddingService()

        categories = Category.objects.all()
        if only_missing:
            existing_ids = CategoryEmbedding.objects.values_list('category_id', flat=True)
            categories = categories.exclude(id__in=existing_ids)   # Skip already-embedded

        for category in categories:
            text = f"{category.name} {category.description}".strip()
            vector = service.generate_embedding(text)
            if vector:
                CategoryEmbedding.objects.update_or_create(
                    category=category,
                    defaults={'embedding_vector': vector}
                )
                self.stdout.write(self.style.SUCCESS(f'CREATED — {category.name}'))
```

**`BaseCommand`**: Django's base class for management commands. Provides `self.stdout.write()` (vs `print`), `self.style.SUCCESS()` (green text), `self.style.ERROR()` (red text).

**`--only-missing`**: `action='store_true'` means the flag is a boolean. When you pass `--only-missing`, `options['only_missing']` is `True`. Without the flag, it's `False`.

**`values_list('category_id', flat=True)`**: Returns `[1, 3, 7, ...]` (list of IDs) instead of `[(1,), (3,), (7,)]`. `flat=True` flattens the tuples.

**`exclude(id__in=existing_ids)`**: SQL: `WHERE id NOT IN (1, 3, 7)`. Skips items that already have embeddings when `--only-missing` is used.

---

### Command 2: `run_kafka_consumer`

```bash
python manage.py run_kafka_consumer
```

> **File**: [management/commands/run_kafka_consumer.py](management/commands/run_kafka_consumer.py)

Starts the Kafka consumer daemon. This is a long-running process (runs until Ctrl+C). In production, it should be run as a separate process (e.g., via `supervisord`, Docker container, or systemd service).

---

## 15. End-to-End Flow: User Views a Product

This is the complete A-to-Z journey of what happens when a user opens a product detail page.

```
User opens: /shop/sony-wh1000xm5 in browser
```

**Step 1 — HTTP Request arrives at Django**
```
GET /store/products/sony-wh1000xm5/
Headers: Authorization: Bearer <jwt_token>
```

**Step 2 — Store view handles the request** (in `store` app, not shown here)
```python
# store/views/product_views.py (simplified)
def retrieve(self, request, *args, **kwargs):
    product = self.get_object()
    
    # Fire custom analytics signal
    from store.signals import product_viewed
    product_viewed.send(
        sender=self.__class__,
        request=request,
        user_id=request.user.id if request.user.is_authenticated else None,
        product_id=product.id,
        product_name=product.name,
    )
    
    return Response(ProductSerializer(product).data)
```

**Step 3 — Insights app catches the signal** (`events/product_events.py`)
```python
@receiver(product_viewed)
def track_product_view(sender, request, user_id, product_id, product_name, **kwargs):
    producer = get_producer()          # Get singleton KafkaEventProducer
    user_info = RequestParserService.extract_user_info(request, request.user)
    producer.send_product_viewed(
        user_id=42,
        product_id=17,
        product_name="Sony WH-1000XM5",
        user_info={"email": "jay@example.com", "ip": "...", ...}
    )
    # This returns quickly — message is now in Kafka
```

**Step 4 — KafkaEventProducer publishes to Kafka**
```python
event = {
    "event_type": "PRODUCT_VIEWED",
    "timestamp": "2026-06-19T10:30:45",
    "user_id": 42,
    "data": {"product_id": 17, "product_name": "Sony WH-1000XM5", ...}
}
self.producer.send('shop.product.viewed', value=event)
# Message now sits in Kafka topic queue
```

**Step 5 — HTTP response returns to user** (while Step 6+ happen in background)
```json
{"product": {"id": 17, "name": "Sony WH-1000XM5", "price": 24999, ...}}
```

User sees the product page immediately. Steps 6+ happen asynchronously.

---

**Step 6 — Kafka Consumer reads the event** (running in background process)
```python
for message in self.consumer:           # This loop was already waiting
    event = message.value               # {"event_type": "PRODUCT_VIEWED", ...}
    self.process_event(message.topic, event)
```

**Step 7 — Consumer calls RecommendationService**
```python
# consumer.py process_event()
user_id = 42
product_id = 17
event_type = "PRODUCT_VIEWED"
RecommendationService.update_user_profile(user_id=42, product_id=17, event_type="PRODUCT_VIEWED")
```

**Step 8 — RecommendationService fetches data**
```python
product = Product.objects.select_related('category').get(id=17)
# product.name = "Sony WH-1000XM5", product.category.name = "Headphones"

prod_emb = ProductEmbedding.objects.filter(product=product).first()
product_vector = prod_emb.embedding_vector  # [0.12, -0.34, 0.89, ...] 768 numbers

profile, _ = UserSemanticProfile.objects.get_or_create(user_id=42, ...)
```

**Step 9 — Update raw interest scores**
```python
weight = EVENT_WEIGHTS['PRODUCT_VIEWED']  # = 1.0

# category_interests before: {"3": 5.0}   (Headphones, score 5.0)
# After:                      {"3": 6.0}   (score increased by 1.0)

# product_interests before: {"17": 0.0}
# After:                    {"17": 1.0}
```

**Step 10 — Merge product vector into user preference vector**
```python
user_vector = profile.preference_vector   # Current user taste vector
product_vector = [0.12, -0.34, 0.89, ...]

# EMA merge (for each of 768 dimensions):
merged[i] = 0.75 * user_vector[i] + 0.25 * 1.0 * product_vector[i]

# Normalize to unit length
profile.preference_vector = normalize(merged)
profile.save()
```

**Step 11 — Next time user calls GET /insights/user-interests/**
```python
user_vector = profile.preference_vector   # Their updated taste vector
all_category_embeddings = CategoryEmbedding.objects.filter(...)

# Compare user vector against every category
scores = [(cat, dot_product(user_vector, cat_embedding)) for cat in all_categories]
# → [("Headphones", 0.945), ("Audio", 0.871), ("Electronics", 0.723), ...]

# Return top 5
```

---

## 16. End-to-End Flow: User Searches for Something

```
User types: "wireless headphones under 3000 in stock"
POST /insights/search/
Body: {"query": "wireless headphones under 3000 in stock"}
```

**Step 1 — SmartSearch.search() called**

**Step 2 — LangChain pipeline parses intent**
```python
# Node 1 (price): matches "under 3000" → price_max = 3000.0
# Node 2 (category): matches "headphone" → category_name = "headphone"
# Node 3 (stock): matches "in stock" → only_in_stock = True
# Node 4 (sort): no sort keywords → sort_by = "relevance"

intent = {
    "price_max": 3000.0,
    "category_name": "headphone",
    "only_in_stock": True,
    "sort_by": "relevance"
}
```

**Step 3 — Generate query embedding**
```python
query_embedding = EmbeddingService().generate_embedding("wireless headphones under 3000 in stock")
# → [0.45, 0.12, -0.89, ...]  768 numbers representing "wireless headphones"
```

**Step 4 — Fetch all product embeddings and filter**
```python
# semantic_threshold = 0.2 (because price + category filters exist)

for each product embedding:
    if product.base_price > 3000: skip           # Hard filter: price
    if "headphone" not in product.category.name: skip  # Hard filter: category
    if product.available_quantity < 1: skip       # Hard filter: stock
    score = cosine_similarity(query_embedding, product_embedding)
    if score < 0.2: skip                          # Semantic filter
    add to results
```

**Step 5 — Sort by relevance (highest similarity first)**
```python
results.sort(key=lambda x: x["similarity_score"], reverse=True)
```

**Step 6 — Return top 16 results**
```json
{
    "message": "Found 4 products under ₹3000 headphone in stock!",
    "results": [
        {"product_name": "boAt Rockerz 450", "base_price": 1299.0, "similarity_score": 0.812, ...},
        {"product_name": "JBL Tune 510BT",   "base_price": 2499.0, "similarity_score": 0.789, ...}
    ]
}
```

---

## 17. Math Reference — Vectors, Similarity, Decay

### L2 Normalization
```
Given: vector v = [3, 4]
magnitude = √(3² + 4²) = √(9 + 16) = √25 = 5
normalized = [3/5, 4/5] = [0.6, 0.8]

Proof: √(0.6² + 0.8²) = √(0.36 + 0.64) = √1.0 = 1.0 ✓
```

### Cosine Similarity via Dot Product (for unit vectors)
```
Since both vectors are normalized (magnitude = 1.0):
  dot(u, v) = |u| × |v| × cos(θ) = 1 × 1 × cos(θ) = cos(θ)

So dot product = cosine similarity for unit vectors.

Example:
  user_vector    = [0.6, 0.0, 0.8]
  product_vector = [0.5, 0.1, 0.9]
  
  dot = (0.6×0.5) + (0.0×0.1) + (0.8×0.9)
      = 0.30 + 0.00 + 0.72
      = 1.02  (would be > 1.0 here because these are not exactly unit vectors, just an illustration)
```

### Exponential Moving Average (EMA)
```
Formula: new[i] = (1 - λ) × old[i] + λ × weight × product[i]
Where λ (DECAY_RATE) = 0.25

Intuition:
  - Old data = 75% influence (preserves historical preferences)
  - New event = 25% × event_weight influence (adds new signal)

  If weight = 10 (ORDER_CREATED):
    new[i] = 0.75 × old[i] + 0.25 × 10 × product[i]
           = 0.75 × old[i] + 2.5  × product[i]
  → Order has 2.5× pull factor

  If weight = 1 (PRODUCT_VIEWED):
    new[i] = 0.75 × old[i] + 0.25 × 1 × product[i]
           = 0.75 × old[i] + 0.25 × product[i]
  → View has only 0.25× pull factor
```

### Stock Status Rules
```
stock == 0        → OUT OF STOCK   (red badge)
stock < 5         → CRITICAL LOW   (orange badge)
stock < 15        → LOW STOCK      (yellow badge)
stock >= 15       → IN STOCK       (green badge)

Restock trigger:
  score >= 5.0 AND stock < 10 → "Restock Immediately"
```

---

## 18. Django Admin Template — How the HTML Dashboard Works

The demand forecast dashboard uses Django's **template inheritance** system:

```
admin/base_site.html          ← Django's built-in admin base
      └── demand_forecast.html ← Our custom template (inherits from base)
```

**Template rendering flow**:
1. Admin hits URL → `ProductDemandAdmin.changelist_view()` runs
2. Builds `context` dict: `{"product_demand": [...], "category_demand": [...]}`
3. Calls `render(request, "admin/insights/demand_forecast.html", context)`
4. Django's template engine:
   - Loads `demand_forecast.html`
   - Sees `{% extends "admin/base_site.html" %}` → loads parent template
   - Fills `{% block content %}` with our HTML
   - Substitutes `{{ item.product.name }}` with actual Python values
   - Returns final HTML string
5. HTML sent to browser

**Template tag reference**:
| Tag | Purpose |
|-----|---------|
| `{% extends "..." %}` | Inherit from another template |
| `{% block name %}...{% endblock %}` | Override a named section |
| `{{ variable }}` | Render a Python variable |
| `{% for x in list %}` | Loop |
| `{% if condition %}` | Conditional |
| `{% empty %}` | Inside for — shown when list is empty |
| `{% load static %}` | Load the `static` tag library |
| `{{ block.super }}` | Include parent block's content |

---

## Quick Setup Reference

```bash
# 1. Start Ollama with the embedding model
ollama pull qwen3-embedding:0.6b
ollama serve

# 2. Start Kafka (requires Docker or local Kafka install)
docker run -p 9092:9092 apache/kafka:latest

# 3. Generate all embeddings (first-time setup)
python manage.py generate_embeddings

# 4. Generate only missing embeddings (incremental update)
python manage.py generate_embeddings --only-missing

# 5. Start the Kafka consumer daemon (keep running in background)
python manage.py run_kafka_consumer

# 6. Test smart search
curl -X POST http://localhost:8000/insights/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "wireless headphones under 3000"}'

# 7. Check user interests (requires auth token)
curl http://localhost:8000/insights/user-interests/ \
  -H "Authorization: Bearer <token>"

# 8. View admin demand dashboard
# Open: http://localhost:8000/admin/ → Insights → Demand & Stock Forecasts
```

---

## Service Dependency Summary

```
SmartSearchView
    └── SmartSearch.search()
            ├── parse_intent()       → LangChain LCEL pipeline (4 nodes)
            ├── EmbeddingService     → Ollama API (localhost:11434)
            └── ProductEmbedding.objects.filter(...)  → Database

UserInterestsView
    └── RecommendationService
            ├── get_top_categories() → CategoryEmbedding.objects.all() + dot_product
            ├── get_top_products()   → ProductEmbedding.objects.all() + dot_product
            └── fallback: category_interests dict

AdminDemandForecastView
    └── UserSemanticProfile.objects.all()  → aggregate all user scores

Kafka Consumer (background)
    └── RecommendationService.update_user_profile()
            ├── ProductEmbedding.objects.filter()
            ├── UserSemanticProfile.objects.get_or_create()
            └── EMA vector merge + normalize + save

Django Signals (on Product/Category save)
    └── EmbeddingService.generate_embedding()
            └── OllamaEmbeddings.embed_query()  → Ollama API
```
