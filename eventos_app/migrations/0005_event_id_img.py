# Generated by Django 5.1 on 2025-06-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos_app', '0004_event_price_alter_notification_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='id_img',
            field=models.CharField(default='sin_imagen', max_length=2083),
        ),
    ]
