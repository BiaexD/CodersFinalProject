from importlib.resources import contents
import pytest
from django.urls import reverse
from rentals.models import Category, Equipment



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



@pytest.mark.django_db
def test_remove_from_cart_view(client):
    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15cm firmy Simond",
        quantity=100,
        price_per_day=2.00,
        deposit=30.00,
    )
    add_url = reverse('add_to_cart', args=[equipment.pk])
    client.post(add_url)
    session = client.session
    assert str(equipment.pk) in session.get('cart', {})

    remove_url = reverse('remove_from_cart', args=[equipment.pk])
    client.post(remove_url)
    session = client.session
    assert str(equipment.pk) not in session.get('cart', {})



@pytest.mark.django_db
def test_increase_quantity_view(client):
    category = Category.objects.create(name="Zima")
    equipment = Equipment.objects.create(
        name="Raki koszykowe",
        category=category,
        description="Rakoi koszykowe firmy Climbing Technology",
        quantity=2,
        price_per_day=10.00,
        deposit=80.00,
    )

    session = client.session
    session['cart'] = {str(equipment.pk): 1}
    session.save()

    url = reverse('increase_quantity', args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('cart')

    session = client.session
    assert session['cart'][str(equipment.id)] == 2

    url = reverse('increase_quantity', args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('cart')

    cart_after = client.session['cart']
    assert cart_after[str(equipment.id)] == 2

    messages = list(response.wsgi_request._messages)
    assert any("Nie mamy więcej" in str(m) for m in messages)



@pytest.mark.django_db
def test_decrease_quantity_adn_remove_view(client):
    category = Category.objects.create(name="Zima")
    equipment = Equipment.objects.create(
        name="Raki koszykowe",
        category=category,
        description="Raki koszykowe firmy Climbing Technology",
        quantity=20,
        price_per_day=10.00,
        deposit=80.00,
    )
    session = client.session
    session['cart'] = {str(equipment.pk): 2}
    session.save()

    url = reverse('decrease_quantity', args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('cart')

    session = client.session
    assert session['cart'][str(equipment.pk)] == 1

    url = reverse('decrease_quantity', args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('cart')

    session = client.session
    assert str(equipment.pk) not in session['cart']