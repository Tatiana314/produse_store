"""
Настройка панели администратора.
"""
from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'icon',
        'image'
    )
    list_editable = ('name', 'slug', 'image')
    search_fields = ('name',)
    readonly_fields = ('icon',)
    save_on_top = True

    @admin.display(description='Изображение')
    def icon(self, category):
        if category.image:
            return mark_safe(f"<img src='{category.image.url}' width=50>")
        return 'Без фото'


@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'category',
        'icon',
        'image'
    )
    search_fields = ('name',)
    list_editable = ('name', 'slug', 'category', 'image')
    list_filter = ('category',)
    readonly_fields = ('icon',)
    save_on_top = True

    @admin.display(description='Изображение')
    def icon(self, subcategory):
        if subcategory.image:
            return mark_safe(f"<img src='{subcategory.image.url}' width=50>")
        return 'Без фото'


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'category',
        'subcategory',
        'price',
        'icon',
        'image',
    )
    search_fields = ('name',)
    list_editable = ('name', 'slug', 'subcategory', 'price', 'image')
    readonly_fields = ('icon', 'category')
    list_filter = ('subcategory',)
    save_on_top = True

    @admin.display(description='Изображение')
    def icon(self, product):
        if product.image:
            return mark_safe(f"<img src='{product.image.url}' width=50>")
        return 'Без фото'

    @admin.display(description='Категория')
    def category(self, product):
        if product.subcategory:
            return product.subcategory
        return 'Без категории'
