import pytest
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from rentals.models import Category, Equipment, Cart, CartItem



@pytest.mark.django_db
def test_cart_context_processor(client_auth, cart, equipment1, equipment2):
    """user, login, category, eq1, eq2, cart"""
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

    url = reverse('order_categories')
    response = client_auth.get(url)
    assert response.status_code == 200

    ctx = response.context
    assert ctx['cart_count'] == 2
    assert ctx['has_active_cart'] is True
    assert ctx ['rental_period']['start_date'] == date(2025, 8, 1)
    assert ctx ['rental_period']['end_date'] == date(2025, 8, 7)
    assert 'Koszyk (2)' in response.content.decode()