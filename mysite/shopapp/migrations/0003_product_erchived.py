# Generated by Django 5.0 on 2023-12-10 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0002_product_created_at_product_discount_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='erchived',
            field=models.BooleanField(default=False),
        ),
    ]
