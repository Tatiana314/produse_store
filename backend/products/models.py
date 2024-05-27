"""
Определение моделей приложения.
"""
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFit

User = get_user_model()
ABSTRACT_DATA = '{name} {slug}'
CART_DATA = '{user}, {products}'
CART_DATA_PRODUCT = '{cart}, {product}, {amount}'
PRODUCT_DATA = '{subcategory} {price}'
SUBCATEGORY = '{category}'


def get_upload_path(instance, filename):
    """Получить путь загрузки для изображения."""
    return f'{instance.__class__.__name__.lower()}/{filename}'


class CreatedModel(models.Model):
    """Абстрактная модель."""

    name = models.CharField('Наименование', max_length=200)
    slug = models.SlugField('Slug-имя', max_length=50, unique=True)
    image = ProcessedImageField(
        upload_to=get_upload_path,
        processors=[ResizeToFit(380, 380)],
        format='JPEG', options={'quality': 70}
    )

    class Meta:
        abstract = True
        ordering = ('id',)

    def __str__(self):
        return ABSTRACT_DATA.format(
            name=self.name,
            slug=self.slug
        )


class Category(CreatedModel):
    """Категория."""

    class Meta(CreatedModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Subcategory(CreatedModel):
    """Подкатегория."""
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='subcategorys',
        verbose_name='Категория',
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return SUBCATEGORY.format(
            category=self.category.name
        ) + super().__str__()


class Product(CreatedModel):
    """Товар."""
    subcategory = models.ForeignKey(
        Subcategory,
        null=True,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name='Подкатегория',
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена'
    )
    image_mid = ImageSpecField(
        source='image',
        processors=[ResizeToFit(100, 100)],
        format='JPEG',
        options={'quality': 60}
    )
    image_mini = ImageSpecField(
        source='image',
        processors=[ResizeToFit(60, 60)],
        format='JPEG',
        options={'quality': 60}
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return PRODUCT_DATA.format(
            subcategory=self.subcategory.name,
            price=self.price
        ) + super().__str__()

    @property
    def images(self):
        return [self.image, self.image_mid, self.image_mini]


class Cart(models.Model):
    """Корзина."""
    products = models.ManyToManyField(
        Product,
        through='CartProduct',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return CART_DATA.format(
            user=self.user.username,
            products=self.products
        )


class CartProduct(models.Model):
    """Модель связи id корзины и id товара."""
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE,
        related_name='products'
    )
    cart = models.ForeignKey(
        Cart,
        verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='cart_products'
    )
    amount = models.IntegerField(
        verbose_name='Кол-во',
        default=1,
        validators=(MinValueValidator(1), MaxValueValidator(5000000))
    )

    class Meta:
        ordering = ('cart',)
        verbose_name = 'Корзина-товар'
        verbose_name_plural = 'Корзина-товары'
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cartproduct',
                violation_error_message='Товар уже добавлен в корзину.'
            )
        ]

    def __str__(self):
        return CART_DATA_PRODUCT.format(
            cart=self.cart,
            product=self.product.name,
            amount=self.amount
        )

    @property
    def purchase(self):
        return self.product.price * self.amount
