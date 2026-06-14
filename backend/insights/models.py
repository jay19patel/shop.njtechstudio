from django.db import models
from store.models import Product


class ProductEmbedding(models.Model):
    """
    Store product embeddings for ML/AI features like recommendations.
    One-to-One relationship with Product model.
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='embedding',
        help_text="Reference to the product"
    )

    # Embedding metadata
    embedding_name = models.CharField(
        max_length=255,
        help_text="Name/identifier for the embedding (e.g., 'product-desc-v1')"
    )

    embedding_version = models.CharField(
        max_length=50,
        default="1.0",
        help_text="Version of the embedding model used"
    )

    # Vector representation (stored as JSON or binary)
    embedding_vector = models.JSONField(
        null=True,
        blank=True,
        help_text="Vector embedding as JSON array (e.g., [0.123, 0.456, ...])"
    )

    # Metadata
    embedding_source = models.CharField(
        max_length=100,
        choices=[
            ('manual', 'Manually Created'),
            ('ai_generated', 'AI Generated'),
            ('ml_model', 'ML Model Generated'),
            ('user_feedback', 'Based on User Feedback'),
        ],
        default='manual',
        help_text="Source of the embedding"
    )

    description = models.TextField(
        blank=True,
        help_text="Description or notes about this embedding"
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="User or system that created the embedding"
    )

    class Meta:
        verbose_name = "Product Embedding"
        verbose_name_plural = "Product Embeddings"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['embedding_name']),
            models.Index(fields=['embedding_source']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.embedding_name}"

