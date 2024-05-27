"""
Настройка сериализации/десереализацией данных.
"""

from rest_framework import serializers

from products.models import Cart, CartProduct, Category, Product, Subcategory


class SubcategoryInfoSerializer(serializers.ModelSerializer):
    """Чтение модели cубкатегория."""
    class Meta:
        exclude = ('category',)
        model = Subcategory


class CategorySerializer(serializers.ModelSerializer):
    """Чтение модели категория."""
    subcategorys = SubcategoryInfoSerializer(many=True, read_only=True,)

    class Meta:
        fields = ('id', 'name', 'slug', 'image', 'subcategorys')
        model = Category


class ProductSerializer(serializers.ModelSerializer):
    """Чтение модели товар."""
    images = serializers.ListSerializer(
        child=serializers.ImageField(), read_only=True
    )

    class Meta:
        fields = ('id', 'name', 'slug', 'images', 'subcategory')
        model = Product
        depth = 2


class CartProductSerializer(serializers.ModelSerializer):
    """Поле продукт при создании/редактировании корзины."""
    id = serializers.IntegerField()

    class Meta:
        fields = ('amount', 'id')
        model = CartProduct

    def validate_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'{value} - продукта не существует.'
            )
        return value


class AmountProductSerializer(serializers.ModelSerializer):
    """Поле продукт/кол-во/стоимость при Get запросе к корзине."""
    id = serializers.ReadOnlyField(source='product.id')
    name = serializers.ReadOnlyField(source='product.name')
    price = serializers.ReadOnlyField(source='product.price')
    purchase = serializers.IntegerField()

    class Meta:
        model = CartProduct
        fields = (
            'id', 'name', 'price', 'amount', 'purchase'
        )


class GetCartSerializer(serializers.ModelSerializer):
    """Корзина."""
    products = AmountProductSerializer(
        many=True, source='cart_products'
    )
    count_product = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'products', 'count_product')
        depth = 1

    def get_count_product(self, obj):
        obj.cart_products.count()
        return obj.cart_products.count()


class CreateUpdateCartSerializer(serializers.ModelSerializer):
    """Создание/редактирование корзины."""
    products = CartProductSerializer(many=True)

    class Meta:
        model = Cart
        depth = 1
        exclude = ('user',)
        read_only_fields = ('user',)

    def validate(self, data):
        if (
            self.context['request'].method in ['POST']
            and Cart.objects.filter(user=self.context['request'].user).exists()
        ):
            raise serializers.ValidationError('Корзина уже существует.')
        products_data = data.get('products')
        if not products_data:
            raise serializers.ValidationError('Необходимо ввести продукт.')
        products = [index['id'] for index in products_data]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                'Продукты не могут повторяться!'
            )
        return data

    def save_products(self, products, cart):
        CartProduct.objects.bulk_create(
            [CartProduct(
                product=Product.objects.get(id=product['id']),
                cart=cart,
                amount=product.get('amount')
            ) for product in products]
        )

    def create(self, validated_data):
        products = validated_data.pop('products')
        cart = Cart.objects.create(**validated_data)
        self.save_products(
            products=products,
            cart=cart
        )
        return cart

    def update(self, instance, validated_data):
        products = validated_data.pop('products')
        instance = super().update(instance, validated_data)
        instance.products.clear()
        self.save_products(
            products=products,
            cart=instance
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return GetCartSerializer(instance, context=context).data


class DeleteProductCartSerializer(serializers.Serializer):
    """Удаление товара из таблицы CartProduct."""
    id_product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )


class ProductCartSerializer(DeleteProductCartSerializer):
    """Добавление товара в таблицу CartProduct."""
    amount = serializers.IntegerField()
