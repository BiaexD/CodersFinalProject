import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rentals.models import Category, Equipment, Cart, CartItem



@pytest.mark.django_db
def test_cart_context_processor(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment1 = Equipment.objects.create(
        name="Ekspres",
        category=category,
        quantity=10,
        price_per_day=2.00,
        deposit=30.0
    )
    equipment2 = Equipment.objects.create(
        name="Crashpad",
        category=category,
        quantity=5,
        price_per_day=15.00,
        deposit=100.0
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-10",
        is_active=True,
    )

    CartItem.objects.create(
        cart=cart,
        equipment=equipment1,
        quantity=3
    )
    CartItem.objects.create(
        cart=cart,
        equipment=equipment2,
        quantity=2
    )

    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert "Koszyk (2)" in response.content.decode()