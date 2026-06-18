from django.contrib import admin
from .models import ProductEmbedding, CategoryEmbedding, UserSemanticProfile, ProductDemand


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


@admin.register(ProductDemand)
class ProductDemandAdmin(admin.ModelAdmin):
    """Admin interface to view product demand forecast and inventory management."""

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import render
        from collections import defaultdict
        from store.models import Product, Category

        # 1. Fetch all semantic profiles
        profiles = UserSemanticProfile.objects.all()

        # 2. Accumulate interest scores across all users
        product_scores = defaultdict(float)
        category_scores = defaultdict(float)

        for profile in profiles:
            for pid, score in (profile.product_interests or {}).items():
                try:
                    product_scores[int(pid)] += float(score)
                except (ValueError, TypeError):
                    pass
            for cid, score in (profile.category_interests or {}).items():
                try:
                    category_scores[int(cid)] += float(score)
                except (ValueError, TypeError):
                    pass

        # 3. Fetch all active products and categories
        products = {p.id: p for p in Product.objects.all().select_related('category')}
        categories = {c.id: c for c in Category.objects.all()}

        # 4. Build product demand report
        product_demand = []
        for pid, score in product_scores.items():
            if pid in products:
                prod = products[pid]
                stock = prod.available_quantity

                # Stock level warning statuses
                if stock == 0:
                    stock_status = "OUT OF STOCK"
                    status_color = "red"
                elif stock < 5:
                    stock_status = "CRITICAL LOW"
                    status_color = "orange"
                elif stock < 15:
                    stock_status = "LOW STOCK"
                    status_color = "yellow"
                else:
                    stock_status = "IN STOCK"
                    status_color = "green"

                # Action recommendation: restock if high demand and low stock
                action = "Restock Immediately" if stock < 10 and score >= 5.0 else "Monitor"

                product_demand.append({
                    "product": prod,
                    "score": round(score, 1),
                    "stock": stock,
                    "stock_status": stock_status,
                    "status_color": status_color,
                    "action": action
                })

        # Sort product list by demand score descending
        product_demand.sort(key=lambda x: x["score"], reverse=True)

        # 5. Build category demand heatmap
        category_demand = []
        for cid, score in category_scores.items():
            if cid in categories:
                cat = categories[cid]
                category_demand.append({
                    "category": cat,
                    "score": round(score, 1)
                })

        # Sort category list by score descending
        category_demand.sort(key=lambda x: x["score"], reverse=True)

        context = {
            **(extra_context or {}),
            "title": "Demand & Stock Forecast",
            "product_demand": product_demand,
            "category_demand": category_demand,
            "opts": self.model._meta,
        }
        return render(request, "admin/insights/demand_forecast.html", context)
