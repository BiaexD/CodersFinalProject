from django.db import models
from django.conf import settings


"""
models.Model oznacza, że ta klasa jest modelem Django, czyli będzie odpowiadać tabeli w bazie danych.

name:
✅ CharField oznacza, że to jest krótki tekst.
✅ max_length=100 mówi, że tekst nie może mieć więcej niż 100 znaków.

description:
✅ TextField służy do przechowywania opisów.
✅ blank=True pozwala zostawić to pole puste przy tworzeniu rekordu.

__str__():
✅ _str_ zwraca tekstową reprezentację obiektu.
✅ Dzięki niej w panelu admina i w konsoli Python zobaczysz nazwę kategorii,
"""
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


"""
category:
✅ Klucz obcy – pole łączące sprzęt z kategorią.
✅ Wskazuje do którego rekordu w tabeli Category należy sprzęt.
✅ on_delete=models.CASCADE - Jeśli usuniesz kategorię, wszystkie sprzęty w tej kategorii też się usuną.

quantity:
✅ Liczba dostępnych sztuk w magazynie.
✅ PositiveIntegerField wymusza, że to musi być liczba ≥0.

price_per_day and deposit:
✅ DecimalField służy do wartości pieniężnych.
-max_digits=5 – maksymalnie 5 cyfr (np. 999.99).
-decimal_places=2 – 2 miejsca po przecinku.
"""
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=5, decimal_places=2)
    deposit = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


"""
Rental:
✅ główna informacja o wypożyczeniu.

STATUS_CHOICES:
✅ Pierwszy element każdej krotki (np. 'pending') zapisywany jest w bazie.
✅ Drugi element (np. 'Oczekujace') wyświetlany w formularzach.

user:
✅ Klucz obcy do tabeli użytkowników (User).
✅ Oznacza, który użytkownik dokonał wypożyczenia.
✅ on_delete=models.CASCADE - jeśli usuniesz użytkownika, usuną się wszystkie jego wypożyczenia.

created_at:
✅ Data i godzina utworzenia rekordu.
✅ auto_now_add=True oznacza - Django automatycznie wstawi bieżącą datę przy tworzeniu.

status:
✅ choices=STATUS_CHOICES – można wybrać tylko spośród podanych opcji.
✅ default='pending' – domyślny status to oczekujące.
"""
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


"""
rental:
✅ klucz obcy do Rental
✅ powiązanie z konkretnym wypożyczeniem
✅ related_name='items' - Dzięki temu możesz napisać: rental.items.all()

equipment:
✅ Klucz obcy do sprzętu.
✅ Mówi, jaki sprzęt jest wypożyczony.

quantity:
✅ Ile sztuk tego sprzętu wypożyczono w tej pozycji.
"""
class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.equipment.name} x {self.quantity}"



