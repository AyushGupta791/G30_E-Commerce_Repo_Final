# Generated by Django 5.2 on 2025-04-15 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Thread_Inn', '0011_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
