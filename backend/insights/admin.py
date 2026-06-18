from django.contrib import admin
from .models import ProductEmbedding, CategoryEmbedding, UserSemanticProfile


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
            'fields': ('description',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CategoryEmbedding)
class CategoryEmbeddingAdmin(admin.ModelAdmin):
    """Admin interface for CategoryEmbedding model."""

    list_display = ('category', 'updated_at')
    search_fields = ('category__name',)
    readonly_fields = ('updated_at',)
    ordering = ('-updated_at',)

    fieldsets = (
        ('Category', {
            'fields': ('category',)
        }),
        ('Vector Data', {
            'fields': ('embedding_vector',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
        }),
    )


@admin.register(UserSemanticProfile)
class UserSemanticProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserSemanticProfile model."""

    list_display = ('user', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)
    ordering = ('-updated_at',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Preference Vector', {
            'fields': ('preference_vector',),
            'classes': ('collapse',)
        }),
        ('Interest Scores', {
            'fields': ('category_interests', 'product_interests'),
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
        }),
    )


