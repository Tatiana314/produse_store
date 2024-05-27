# Generated by Django 5.0.6 on 2024-05-23 17:47

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_category_image_alter_product_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='product',
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
            model_name='subcategory',
            name='image',
            field=models.ImageField(upload_to='products/subcategorys/', verbose_name='Изображение'),
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Кол-во')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_products', to='products.cart', verbose_name='Корзина')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Корзина-продукт',
                'verbose_name_plural': 'Корзин-продуктты',
                'ordering': ('cart',),
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ManyToManyField(through='products.CartProduct', to='products.product', verbose_name='Продукт'),
        ),
        migrations.AddConstraint(
            model_name='cartproduct',
            constraint=models.UniqueConstraint(fields=('cart', 'product'), name='unique_cartproduct', violation_error_message='Продукт уже добавлен в корзину.'),
        ),
    ]