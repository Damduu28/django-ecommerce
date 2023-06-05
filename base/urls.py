from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.homePage, name="home"),
    path('store/', views.storePage, name="store"),
    path('checkout/', views.checkoutPage, name="checkout"),
    path('cart/', views.cartPage, name="cart"),
    path('product/<slug:slug>/', views.productPage, name="product"),
    path('update-cart/', views.updateCart, name="update-cart"),
    path('apply-coupon/', views.applyCoupon, name="apply-coupon"),
    path('change-category/', views.changeCategory, name="change-category"),
    path('news-letter/', views.newsLetter, name="news-letter"),
    path('review-product/<slug:slug>/', views.reviewProduct, name="review-product"),
]