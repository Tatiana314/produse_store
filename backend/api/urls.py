"""
Конфигурация URL-адреса для API проекта produse_store.
"""
from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CategoryViewSet, ProductViewSet

app_name = 'api'
VERSION = 'v1'


router_1 = DefaultRouter()

router_1.register('categorys', CategoryViewSet, basename='categorys')
router_1.register('products', ProductViewSet, basename='products')
router_1.register('carts', CartViewSet, basename='carts')

urlpatterns = [
    path(f'{VERSION}/', include((router_1.urls))),
    path(f'{VERSION}/api-token-auth/', views.obtain_auth_token),
]
