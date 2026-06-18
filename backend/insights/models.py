from django.db import models
from django.conf import settings
from store.models import Product, Category


class ProductEmbedding(models.Model):
    """Stores Ollama embedding vector for product semantic search."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='embedding'
    )

    embedding_name = models.CharField(
        max_length=255,
        default="qwen3-embedding"
    )

    embedding_version = models.CharField(
        max_length=50,
        default="0.6b"
    )

    embedding_vector = models.JSONField(
        null=True,
        blank=True
    )

    embedding_source = models.CharField(
        max_length=100,
        choices=[
            ('ollama', 'Ollama Local'),
            ('manual', 'Manual'),
        ],
        default='ollama'
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Embedding"
        verbose_name_plural = "Product Embeddings"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['embedding_source']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.embedding_name}"


class CategoryEmbedding(models.Model):
    """Stores Ollama embedding vector for category semantic matching."""

    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='embedding'
    )

    embedding_vector = models.JSONField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category Embedding"
        verbose_name_plural = "Category Embeddings"

    def __str__(self) -> str:
        return f"{self.category.name} Embedding"


class UserSemanticProfile(models.Model):
    """Stores the aggregated user interest preference vector and raw scores."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='semantic_profile'
    )

    # N-dimensional float array representing the user preference, normalized to unit length
    preference_vector = models.JSONField(
        null=True,
        blank=True
    )

    # Key-value maps: { "category_id": score }
    category_interests = models.JSONField(
        default=dict,
        blank=True
    )

    # Key-value maps: { "product_id": score }
    product_interests = models.JSONField(
        default=dict,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Semantic Profile"
        verbose_name_plural = "User Semantic Profiles"

    def __str__(self) -> str:
        return f"Semantic Profile - {self.user.username}"
