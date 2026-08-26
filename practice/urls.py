from django.urls import path
from . import views

urlpatterns = [
    path('visits/', views.visits_view, name='visits'),
    path('visits/reset/', views.visits_reset, name='visits_reset'),
    path('products/', views.products_view, name='products'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('promo/', views.promo_generate, name='promo_generate'),
    path('promo/check/', views.promo_check, name='promo_check'),
]