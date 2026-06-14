# Generated migration for ProductEmbedding model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductEmbedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding_name', models.CharField(help_text='Name/identifier for the embedding (e.g., \'product-desc-v1\')', max_length=255)),
                ('embedding_version', models.CharField(default='1.0', help_text='Version of the embedding model used', max_length=50)),
                ('embedding_vector', models.JSONField(blank=True, help_text='Vector embedding as JSON array (e.g., [0.123, 0.456, ...])', null=True)),
                ('embedding_source', models.CharField(choices=[('manual', 'Manually Created'), ('ai_generated', 'AI Generated'), ('ml_model', 'ML Model Generated'), ('user_feedback', 'Based on User Feedback')], default='manual', help_text='Source of the embedding', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Description or notes about this embedding')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, help_text='User or system that created the embedding', max_length=255)),
                ('product', models.OneToOneField(help_text='Reference to the product', on_delete=django.db.models.deletion.CASCADE, related_name='embedding', to='store.product')),
            ],
            options={
                'verbose_name': 'Product Embedding',
                'verbose_name_plural': 'Product Embeddings',
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['embedding_name'], name='insights_pro_embeddi_idx'),
                    models.Index(fields=['embedding_source'], name='insights_pro_embeddi_2_idx'),
                    models.Index(fields=['-updated_at'], name='insights_pro_updated_idx'),
                ],
            },
        ),
    ]
