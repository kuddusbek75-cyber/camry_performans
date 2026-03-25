from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('dept/<str:dept_key>/', views.department, name='department'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
