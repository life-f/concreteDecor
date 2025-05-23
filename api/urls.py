from django.urls import path

from api.views import CustomUserUpdateView, PromoCodeCheckView, CartView, OrdersView, CreateOrderView, SeriesDetailView, \
    CartTotalSum
from api.views.category import CategoryListView
from api.views.product import ProductCatalogView

urlpatterns = [
    path('users/me/', CustomUserUpdateView.as_view(), name='user-update'),
    path('products/', ProductCatalogView.as_view(), name='product-catalog'),
    path('products/<int:id>/', ProductCatalogView.as_view(), name='product-catalog'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('promo/check/', PromoCodeCheckView.as_view(), name='promo-code-check'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/total/', CartTotalSum.as_view(), name='cart-total'),
    path('orders/', OrdersView.as_view(), name='order'),
    path('order/create/', CreateOrderView.as_view(), name='create-order'),
    path('series/<int:id>/', SeriesDetailView.as_view(), name='series-detail'),
]
