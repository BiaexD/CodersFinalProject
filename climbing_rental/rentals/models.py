from django.db import models
from django.conf import settings
from django.contrib.auth.models import User



class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



class Equipment(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField(default=0)
    price_per_day = models.DecimalField(max_digits=5, decimal_places=2)
    deposit = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name



class Rental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Oczekujace'),
        ('active', 'Aktywne'),
        ('finished', 'Zakonczone'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.start_date} - {self.end_date}"



class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.equipment.name} x {self.quantity}"



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Koszyk {self.user.username} ({self.start_date} - {self.end_date})"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.equipment.name} x {self.quantity}"



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_number = models.CharField(max_length=20, verbose_name="Numer legitymacji KW Poznan", blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="Numer kontaktory")

    def __str__(self):
        return f"Profil {self.user.username}"