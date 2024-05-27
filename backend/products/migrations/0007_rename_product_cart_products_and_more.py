# Generated by Django 5.0.6 on 2024-05-26 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_product_image_big_alter_product_image_min'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='product',
            new_name='products',
        ),
        migrations.RemoveField(
            model_name='product',
            name='image_min',
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(upload_to='products/categorys/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='products/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image_big',
            field=models.ImageField(default='image_min', upload_to='products/', verbose_name='Изображение большое'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='image',
            field=models.ImageField(upload_to='products/subcategorys/', verbose_name='Изображение'),
        ),
    ]
