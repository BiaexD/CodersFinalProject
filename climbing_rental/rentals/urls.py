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
from django.urls import path        #funkcja path definiuje adresy URL
from rentals import views


"""
path:
URL: "equipment/'
Widok: views.equipment_list
Nazwa: equipment_list (mozna uzywac ja w linkach)
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:equipment_id>', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:equipment_id>', views.remove_from_cart, name='remove_from_cart'),
]