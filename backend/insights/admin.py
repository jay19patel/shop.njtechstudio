from django.contrib import admin
from .models import ProductEmbedding


@admin.register(ProductEmbedding)
class ProductEmbeddingAdmin(admin.ModelAdmin):
    """Admin interface for ProductEmbedding model."""

    list_display = ('product', 'embedding_name', 'embedding_version', 'embedding_source', 'updated_at')
    list_filter = ('embedding_source', 'embedding_version', 'created_at', 'updated_at')
    search_fields = ('product__name', 'embedding_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('Embedding Info', {
            'fields': ('embedding_name', 'embedding_version', 'embedding_source')
        }),
        ('Vector Data', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('description', 'created_by'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
