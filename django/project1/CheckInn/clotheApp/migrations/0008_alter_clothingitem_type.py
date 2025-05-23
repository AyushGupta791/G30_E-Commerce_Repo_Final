# Generated by Django 5.2 on 2025-04-14 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clotheApp', '0007_alter_clothingitem_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clothingitem',
            name='type',
            field=models.CharField(choices=[('T-Shirts', 'T-Shirts'), ('shirts', 'Shirts'), ('jackets', 'Jackets'), ('hoodies', 'Hoodies'), ('sweatshirts', 'Sweatshirts'), ('jeans', 'Jeans'), ('trousers', 'Trousers'), ('shorts', 'Shorts'), ('joggers', 'Joggers'), ('capris', 'Capris'), ('casual', 'Casual'), ('boots', 'Boots'), ('sandals', 'Sandals'), ('formal', 'Formal'), ('sports', 'Sports'), ('hats', 'Hats'), ('glasses', 'Glasses'), ('belts', 'Belts'), ('jewelry', 'Jewlery'), ('watches', 'Watches')], max_length=50),
        ),
    ]
