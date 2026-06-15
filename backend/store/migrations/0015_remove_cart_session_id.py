from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_add_price_snapshot_to_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='session_id',
        ),
    ]
