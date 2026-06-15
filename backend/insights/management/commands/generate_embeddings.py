from django.core.management.base import BaseCommand
from store.models import Product
from insights.models import ProductEmbedding
from insights.utils import EmbeddingService


class Command(BaseCommand):
    help = 'Generate or update embeddings for all existing products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Only generate for products that do not have an embedding yet',
        )

    def handle(self, *args, **options):
        only_missing = options['only_missing']
        service = EmbeddingService()

        products = Product.objects.filter(is_active=True).select_related('category')

        if only_missing:
            existing_ids = ProductEmbedding.objects.values_list('product_id', flat=True)
            products = products.exclude(id__in=existing_ids)

        total = products.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No products to process.'))
            return

        self.stdout.write(f'Processing {total} product{"s" if total != 1 else ""}...\n')

        created_count = 0
        updated_count = 0
        failed_count = 0

        for i, product in enumerate(products, start=1):
            text = f"{product.name} {product.description}"
            vector = service.generate_embedding(text)

            if vector is None:
                self.stdout.write(self.style.ERROR(f'  [{i}/{total}] FAILED  — {product.name}'))
                failed_count += 1
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
            self.stdout.write(self.style.SUCCESS(f'  [{i}/{total}] {label}  — {product.name}'))

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write('\n' + '─' * 40)
        self.stdout.write(self.style.SUCCESS(f'  Created : {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Updated : {updated_count}'))
        if failed_count:
            self.stdout.write(self.style.ERROR(f'  Failed  : {failed_count}'))
        self.stdout.write('─' * 40)
