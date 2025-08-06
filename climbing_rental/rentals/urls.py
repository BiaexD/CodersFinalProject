"""
URL configuration for climbing_rental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rentals import views


urlpatterns = [
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:equipment_id>', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:equipment_id>', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:equipment_id>', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:equipment_id>', views.decrease_quantity, name='decrease_quantity'),
    path('order/', views.order_summary, name='order_summary'),
    path('user-panel/', views.user_panel, name='user_panel'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('select-dates/', views.select_dates, name='select_dates'),
    path('my_rentals/', views.user_rentals, name='user_rentals'),
    path('my_rentals/<int:rental_id>/finish/', views.finish_rental, name='finish_rental'),
]