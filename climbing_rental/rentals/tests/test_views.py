import pytest
from django.urls import reverse
from rentals.models import Category, Equipment


"""
@pytest.mark.django_db - dekorator mowi pytestowi ze ten test bedzie korzystal z bazy danych

client - to specjalny obiekt dostarczany przez django ktory symuluje przegladarne (GET, POST itp)

category - tworzymy kategoriw, bo sprzet musi byc do niej przypisany (ForeignKey)

Equipment.objects.create(...) - tworzymy sprzet, dzieki temu widok ma co wyswietlic

url - pobieramy sciezke /equipment/

seponse - wysylamy symulowane zadanie GET

assert response 200 - sprawdzamy czy serwer zwrocil OK

assert "Lina Beal" - sprawdzamy czy nazwa sprzetu pojawila sie w HTML
"""

@pytest.mark.django_db
def test_equipment_list_view(client):
    category = Category.objects.create(name="Liny")
    Equipment.objects.create(
        name="Lina Beal",
        category=category,
        quantity=5,
        price_per_day=6.00,
        deposit=100.00,
    )
    url = reverse("equipment_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "Lina Beal" in response.content.decode()



@pytest.mark.django_db
def test_equipment_detail_view(client):
    category = Category.objects.create(name="Kaski")
    equipment = Equipment.objects.create(
        name="Kask",
        category=category,
        description="Kask Petzl",
        quantity=10,
        price_per_day=5.00,
        deposit=50.00,
    )
    url = reverse("equipment_detail", args=[equipment.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "Kask Petzl" in response.content.decode()


