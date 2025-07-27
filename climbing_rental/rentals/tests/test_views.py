from importlib.resources import contents

import pytest
from django.urls import reverse
from rentals.models import Category, Equipment
from django.shortcuts import render
from django.contrib.auth.models import User


"""
@pytest.mark.django_db - dekorator mowi pytestowi ze ten test bedzie korzystal z bazy danych

client - to specjalny obiekt dostarczany przez django ktory symuluje przegladarne (GET, POST itp)

category - tworzymy kategoriw, bo sprzet musi byc do niej przypisany (ForeignKey)

Equipment.objects.create(...) - tworzymy sprzet, dzieki temu widok ma co wyswietlic

url - pobieramy sciezke /equipment/

response - wysylamy symulowane zadanie GET(get pokazuje nam cos)

assert response 200 - sprawdzamy czy serwer zwrocil OK

assert "Lina Beal" - sprawdzamy czy nazwa sprzetu pojawila sie w HTML

response.content – to surowy HTML w bajtach (b'<html>...').
.decode() zamienia go na zwykły tekst ('<html>...'), żebyśmy mogli go przeszukać.
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



@pytest.mark.django_db
def test_category_detail_view(client):
    category1 = Category.objects.create(name="Zima")
    category2 = Category.objects.create(name="Skaly")
    Equipment.objects.create(
        name="Raki koszykowe",
        category=category1,
        description="Raki koszykowe firmy Climbing Technology",
        quantity=10,
        price_per_day=10.00,
        deposit=100.00,
    )
    Equipment.objects.create(
        name="Ekspres",
        category=category2,
        description="Ekspres 15cm firmy Simond",
        quantity=100,
        price_per_day=2.00,
        deposit=30.00,
    )
    url1 = reverse('category_detail', args=[category1.pk])
    response1 = client.get(url1)
    assert response1.status_code ==200

    content1 = response1.content.decode()
    assert "Raki koszykowe" in content1
    assert "Ekspres" not in content1

    url2 = reverse('category_detail', args=[category2.pk])
    response2 = client.get(url2)
    assert response2.status_code ==200

    content2 = response2.content.decode()
    assert "Raki koszykowe" not in content2
    assert "Ekspres" in content2



@pytest.mark.django_db
def test_home_view(client):
    Category.objects.create(name="Zima")
    Category.objects.create(name="Skaly")
    Category.objects.create(name="Via ferrata")

    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "Zima" in content
    assert "Skaly" in content
    assert "Via ferrata" in content


"""
client.session - pobieramy dane z sesji testowego uzytkownika (cos na ksztalt ciasteczek) - Django przechowuje koszyk w tej sesji – w postaci słownika (dict).
session['cart'] - dodajemy 2 sprzety do koszyka tak jakby klient umiescil je za pomoca dodaj
session.save() - zapisujemy te zmiany w sesji

url = reverse('cart') – funkcja Django, która tłumaczy nazwę ścieżki (cart) na jej prawdziwy adres URL
client.get(url) - symulujemy wejscie na strone uzytkownika /cart/
"""
@pytest.mark.django_db
def test_cart_view(client):
    category = Category.objects.create(name="Zima")
    equipment = Equipment.objects.create(
        name="Raki koszykowe",
        category=category,
        description="Raki koszykowe firmy Climbing Technology",
        quantity=10,
        price_per_day=10.00,
        deposit=100.00,
    )
    session = client.session
    session['cart'] = {str(equipment.pk): 2}
    session.save()

    url = reverse('cart')
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "Raki koszykowe" in content
    assert "2" in content
    assert "20.00" in content
    assert "200.00" in content


"""
args=[equipment.pk]:
- oznacza, że podstawiamy ID naszego sprzętu do ścieżki URL.

client.post(url):
- To jest POST, czyli wysyłamy formularz – tak jakbyśmy kliknęli przycisk „Dodaj do koszyka”.
- symuluje wysylanie formularza

response.status_code == 302:
- sprawdzamy czy nasz post zadzialal i wlozyl cos do koszyka

session = client.session:
- Otwieramy „plecak użytkownika” – czyli sesję.
- Django przechowuje koszyk w tej sesji – w postaci słownika (dict).

cart = session.get('cart', {}):
- Pobieramy zawartość koszyka z sesji.
- Jeśli koszyka nie ma (pierwsze użycie) – dostaniemy pusty słownik {}.
                               
assert str(equipment.pk) in cart:
- Sprawdzamy, czy nasz sprzęt jest w koszyku.
- equipment.pk to ID sprzętu, np. 3, ale koszyk przechowuje to jako tekst '3', więc musimy zrobić str(...)

assert cart[str(equipment.pk)] == 1:
- Sprawdzamy, czy ilość danego sprzętu w koszyku wynosi 1.
- Bo raz kliknęliśmy „Dodaj do koszyka”, więc powinien być 1.
"""
@pytest.mark.django_db
def test_add_to_cart_view(client):
    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15cm firmy Simond",
        quantity=100,
        price_per_day=2.00,
        deposit=30.00,
    )
    url = reverse('add_to_cart', args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302

    session = client.session
    cart = session.get('cart', {})
    assert str(equipment.pk) in cart
    assert cart[str(equipment.pk)] == 1