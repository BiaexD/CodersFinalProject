from django.contrib import admin
from .models import Category, Equipment, Rental, RentalItem, Cart, CartItem, UserProfile

admin.site.register(Category)
admin.site.register(Equipment)
admin.site.register(Rental)
admin.site.register(RentalItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserProfile)