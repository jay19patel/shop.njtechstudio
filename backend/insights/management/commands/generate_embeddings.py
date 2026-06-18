from django.core.management.base import BaseCommand
from typing import Any
from store.models import Product, Category
from insights.models import ProductEmbedding, CategoryEmbedding
from insights.services.embeddings import EmbeddingService


class Command(BaseCommand):
    """Django management command to generate category and product embeddings using Ollama."""

    help = 'Generate or update embeddings for all existing products and categories'

    def add_arguments(self, parser: Any) -> None:
        """Add options to the parser."""
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Only generate for items that do not have an embedding yet',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        only_missing = options['only_missing']
        service = EmbeddingService()

        # ─── CATEGORIES ───
        self.stdout.write(self.style.MIGRATE_HEADING('=== Category Embeddings ==='))
        categories = Category.objects.all()

        if only_missing:
            existing_cat_ids = CategoryEmbedding.objects.values_list('category_id', flat=True)
            categories = categories.exclude(id__in=existing_cat_ids)

        cat_total = categories.count()

        if cat_total == 0:
            self.stdout.write(self.style.WARNING('No categories to process.'))
        else:
            self.stdout.write(f'Processing {cat_total} category{"ies" if cat_total != 1 else ""}...\n')
            cat_created = 0
            cat_updated = 0
            cat_failed = 0

            for i, category in enumerate(categories, start=1):
                text = f"{category.name} {category.description}".strip()
                vector = service.generate_embedding(text)

                if vector is None:
                    self.stdout.write(self.style.ERROR(f'  [{i}/{cat_total}] FAILED  — {category.name}'))
                    cat_failed += 1
                    continue

                _, created = CategoryEmbedding.objects.update_or_create(
                    category=category,
                    defaults={
                        'embedding_vector': vector,
                    }
                )

                label = 'CREATED' if created else 'UPDATED'
                self.stdout.write(self.style.SUCCESS(f'  [{i}/{cat_total}] {label}  — {category.name}'))

                if created:
                    cat_created += 1
                else:
                    cat_updated += 1

            self.stdout.write('\n' + '─' * 40)
            self.stdout.write(self.style.SUCCESS(f'  Categories Created : {cat_created}'))
            self.stdout.write(self.style.SUCCESS(f'  Categories Updated : {cat_updated}'))
            if cat_failed:
                self.stdout.write(self.style.ERROR(f'  Categories Failed  : {cat_failed}'))
            self.stdout.write('─' * 40 + '\n')

        # ─── PRODUCTS ───
        self.stdout.write(self.style.MIGRATE_HEADING('=== Product Embeddings ==='))
        products = Product.objects.filter(is_active=True).select_related('category')

        if only_missing:
            existing_prod_ids = ProductEmbedding.objects.values_list('product_id', flat=True)
            products = products.exclude(id__in=existing_prod_ids)

        prod_total = products.count()

        if prod_total == 0:
            self.stdout.write(self.style.WARNING('No products to process.'))
        else:
            self.stdout.write(f'Processing {prod_total} product{"s" if prod_total != 1 else ""}...\n')
            prod_created = 0
            prod_updated = 0
            prod_failed = 0

            for i, product in enumerate(products, start=1):
                text = f"{product.name} {product.description}".strip()
                vector = service.generate_embedding(text)

                if vector is None:
                    self.stdout.write(self.style.ERROR(f'  [{i}/{prod_total}] FAILED  — {product.name}'))
                    prod_failed += 1
                    continue

                _, created = ProductEmbedding.objects.update_or_create(
                    product=product,
                    defaults={
                        'embedding_vector': vector,
                        'embedding_source': 'ollama',
                        'description': f'Auto-generated for: {product.name}',
                    }
                )

                label = 'CREATED' if created else 'UPDATED'
                self.stdout.write(self.style.SUCCESS(f'  [{i}/{prod_total}] {label}  — {product.name}'))

                if created:
                    prod_created += 1
                else:
                    prod_updated += 1

            self.stdout.write('\n' + '─' * 40)
            self.stdout.write(self.style.SUCCESS(f'  Products Created : {prod_created}'))
            self.stdout.write(self.style.SUCCESS(f'  Products Updated : {prod_updated}'))
            if prod_failed:
                self.stdout.write(self.style.ERROR(f'  Products Failed  : {prod_failed}'))
            self.stdout.write('─' * 40)
