# Generated by Django 5.0 on 2023-12-14 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0003_product_erchived'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='erchived',
            new_name='archived',
        ),
    ]
