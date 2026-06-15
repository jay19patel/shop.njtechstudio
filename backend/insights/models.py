from django.db import models
from store.models import Product


class ProductEmbedding(models.Model):
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

    def __str__(self):
        return f"{self.product.name} - {self.embedding_name}"

