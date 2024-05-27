"""
Логика работы API.
"""
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import Author
from api.serializers import (AmountProductSerializer, CategorySerializer,
                             CreateUpdateCartSerializer,
                             DeleteProductCartSerializer, GetCartSerializer,
                             ProductCartSerializer, ProductSerializer)
from products.models import CartProduct, Category, Product, User

DELETE_PRODUCT = 'Товар удален из корзины'
CART_EMPTY = 'Все товары удалены из корзины'
ERROR_AMOUNT = 'Количество не может быть меньше 1.'


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Чтение списка/объекта категория."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Чтение списка/объекта товар."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)


class CartViewSet(viewsets.ModelViewSet):
    """CRUD модели - корзина."""
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'create')

    def get_serializer_class(self):
        if self.action in ('list',):
            return GetCartSerializer
        return CreateUpdateCartSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return user.users.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(request_body=ProductCartSerializer,
                         responses={201: AmountProductSerializer})
    @action(
        permission_classes=(Author,),
        methods=('post',), detail=True
    )
    def product_cart(self, request, pk=None):
        """Добавляем продукт в корзину."""
        cart = self.get_object()
        product = get_object_or_404(Product, id=request.data.get('id_product'))
        amount = request.data.get('amount')
        if amount < 1:
            return Response(
                {'errors': ERROR_AMOUNT},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_product, created = CartProduct.objects.get_or_create(
            cart=cart, product=product
        )
        cart_product.amount = amount
        cart_product.save(update_fields=['amount'])
        return Response(
            AmountProductSerializer(cart_product).data,
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(request_body=DeleteProductCartSerializer,
                         responses={204: DELETE_PRODUCT})
    @product_cart.mapping.delete
    def delete_product_cart(self, request, pk=None):
        """Удаляем продукт из корзины."""
        cart = self.get_object()
        cart.cart_products.filter(
            product=request.data.get('id_product')
        ).delete()
        return Response(DELETE_PRODUCT, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(responses={204: CART_EMPTY})
    @action(
        permission_classes=(Author,),
        methods=('delete',), detail=True
    )
    def clean_all(self, request, pk=None):
        """Полная очистка корзины."""
        cart = self.get_object()
        self.perform_destroy(
            cart.cart_products.all()
        )
        return Response(CART_EMPTY,
                        status=status.HTTP_204_NO_CONTENT)
