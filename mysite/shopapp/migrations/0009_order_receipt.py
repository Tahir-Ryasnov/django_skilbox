# Generated by Django 5.0.1 on 2024-02-18 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0008_product_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='receipt',
            field=models.FileField(null=True, upload_to='orders/receipts/'),
        ),
    ]
