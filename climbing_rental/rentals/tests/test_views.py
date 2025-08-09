import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rentals.models import Category, Equipment, Cart, CartItem, Rental, RentalItem, UserProfile


@pytest.mark.django_db
def test_equipment_list_view(client, equipment1):
    """category, Equipment"""
    url = reverse('equipment_list')
    response = client.get(url)
    assert response.status_code == 200
    assert 'Ekspres' in response.content.decode()



@pytest.mark.django_db
def test_equipment_detail_view(client, equipment1):
    """category, Equipment"""
    url = reverse('equipment_detail', args=[equipment1.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'Ekspres' in response.content.decode()
    assert 'Ekspres 15cm' in response.content.decode()



@pytest.mark.django_db
def test_category_detail_shows_only_available_equipment(client_auth, cart, equipment1, equipment2):
    """user, login, category, eq1, eq2, cart"""
    CartItem.objects.create(cart=cart, equipment=equipment2, quantity=equipment2.quantity)

    url = reverse('category_detail', args=[equipment1.category.pk])
    response = client_auth.get(url)

    assert response.status_code == 200
    assert 'Ekspres' in response.content.decode()
    assert 'Crashpad' not in response.content.decode()



@pytest.mark.django_db
def test_cart_view(client_auth, cart, equipment1, equipment2):
    """user, login, category, eq1, eq2, cart"""
    CartItem.objects.create(
        cart=cart,
        equipment=equipment1,
        quantity=2,
    )
    CartItem.objects.create(
        cart=cart,
        equipment=equipment2,
        quantity=1,
    )

    url = reverse('cart')
    response = client_auth.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Ekspres" in content
    assert "Crashpad" in content
    assert "2" in content
    assert "1" in content
    assert "20.0" in content or "20.00" in content
    assert "160.0" in content or "160.00" in content



@pytest.mark.django_db
def test_add_to_cart_view(client_auth, cart, equipment1):
    """user, login, category, eq1, cart"""
    assert not CartItem.objects.filter(cart=cart, equipment=equipment1).exists()

    url = reverse("add_to_cart", args=[equipment1.pk])
    for i in range(10):
        response = client_auth.post(url)
        assert response.status_code == 302

    cart_item = CartItem.objects.get(cart=cart, equipment=equipment1)
    assert cart_item.quantity == 10

    response = client_auth.post(url)
    assert response.status_code == 302
    cart_item.refresh_from_db()
    assert cart_item.quantity == 10
    messages = list(response.wsgi_request._messages)
    assert any("nie mozna dodac wiecej" in str(m).lower() for m in messages)



@pytest.mark.django_db
def test_remove_from_cart_view(client_auth, cart, equipment1):
    """user, login, category, eq1, cart"""
    CartItem.objects.create(cart=cart, equipment=equipment1, quantity=2)

    url = reverse("remove_from_cart", args=[equipment1.pk])
    response = client_auth.post(url)
    assert response.status_code == 302
    assert not CartItem.objects.filter(cart=cart, equipment=equipment1).exists()



@pytest.mark.django_db
def test_increase_quantity_view(client_auth, cart, equipment1):
    """user, login, category, eq1, cart"""
    cart_item = CartItem.objects.create(cart=cart, equipment=equipment1, quantity=4)

    url = reverse("increase_quantity", args=[equipment1.pk])
    response = client_auth.post(url)
    assert response.status_code == 302

    cart_item.refresh_from_db()
    assert cart_item.quantity == 5
    for i in range(6):
        response = client_auth.post(url)
        assert response.status_code == 302

    cart_item.refresh_from_db()
    assert cart_item.quantity == 10
    messages = list(response.wsgi_request._messages)
    assert any("nie mamy więcej" in str(m).lower() for m in messages)



@pytest.mark.django_db
def test_decrease_quantity_adn_remove_view(client_auth, cart, equipment1):
    """user, login, category, eq1, cart"""
    cart_item = CartItem.objects.create(cart=cart, equipment=equipment1, quantity=2)
    url = reverse("decrease_quantity", args=[equipment1.pk])

    response = client_auth.post(url)
    assert response.status_code == 302

    cart_item.refresh_from_db()
    assert cart_item.quantity == 1

    response = client_auth.post(url)
    assert response.status_code == 302
    assert not CartItem.objects.filter(cart=cart, equipment=equipment1).exists()



@pytest.mark.django_db
def test_select_dates_desactivates_previous_cart(client_auth, user):
    """user, login"""
    old_cart = Cart.objects.create(
        user=user,
        start_date="2025-08-10",
        end_date="2025-08-15",
        is_active=True,
    )

    url = reverse('select_dates')
    response = client_auth.post(url, {
        'start_date': '2025-09-01',
        'end_date': '2025-09-05',
    })
    assert response.status_code == 302

    old_cart.refresh_from_db()
    assert old_cart.is_active == False

    new_cart = Cart.objects.get(user=user, is_active=True)
    assert str(new_cart.start_date) == "2025-09-01"
    assert str(new_cart.end_date) == "2025-09-05"



def test_user_rentals_view(client_auth, user):
    """user, login"""
    Rental.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-15",
        status="pending",
    )

    url = reverse('user_rentals')
    response = client_auth.get(url)
    assert response.status_code == 200
    assert "2025-08-01" in response.content.decode()
    assert "2025-08-15" in response.content.decode()



def test_order_summary_view(client_auth, user, equipment1, cart):
    """user, login, category, eq1, cart"""
    CartItem.objects.create(
        cart=cart,
        equipment=equipment1,
        quantity=2
    )

    url = reverse('order_summary')
    response = client_auth.get(url)
    assert response.status_code == 200
    assert "Ekspres" in response.content.decode()

    response = client_auth.post(url)
    assert response.status_code == 302

    cart.refresh_from_db()
    assert cart.is_active is False



@pytest.mark.django_db
def test_finish_rental_view(client_auth, equipment1, rental_with_item):
    """user, login, category, eq1, rental, rental_with_item"""
    equipment1.quantity -= 2
    equipment1.save()

    url = reverse('finish_rental', args=[equipment1.pk])
    response = client_auth.get(url)
    assert response.status_code == 302

    rental_with_item.refresh_from_db()
    assert rental_with_item.status == "finished"

    equipment1.refresh_from_db()
    assert equipment1.quantity == 10

    messages = list(response.wsgi_request._messages)
    assert any("zostalo zakonczone" in str(m) for m in messages)



@pytest.mark.django_db
def test_rental_detail_view(client_auth, rental_with_item):
    """user, login, category, eq1, rental, rental_with_item"""
    url = reverse('rental_detail', args=[rental_with_item.pk])
    response = client_auth.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ekspres" in content
    assert "2025-08-01" in content
    assert "ilosc: 2" in content



@pytest.mark.django_db
def test_user_data_view(client_auth, user, user_profile):
    """user, login, user_profile"""
    # UserProfile.objects.create(
    #     user=user,
    #     membership_number='9999',
    #     phone_number='123456789',
    # )

    url = reverse('user_data')
    response = client_auth.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "Jan" in content
    assert "Kowalski" in content
    assert "jan@kowalski.pl" in content
    assert "9999" in content
    assert "123456789" in content
    assert "Edytuj" in content



@pytest.mark.django_db
def test_user_edit_data_view(client_auth, user, user_profile):
    """user, login, user_profile"""
    # UserProfile.objects.create(
    #     user=user,
    #     membership_number='9999',
    #     phone_number='123456789',
    # )

    new_data = {
        'first_name': 'Adam',
        'last_name': 'Nowak',
        'email': 'adam@nowak.pl',
        'membership_number': '0000',
        'phone_number': '987654321',
    }

    url = reverse('user_edit_data')
    response = client_auth.post(url, {
        'first_name': new_data['first_name'],
        'last_name': new_data['last_name'],
        'email': new_data['email'],
        'membership_number': new_data['membership_number'],
        'phone_number': new_data['phone_number'],
    })

    assert response.status_code == 302

    user.refresh_from_db()
    profile = UserProfile.objects.get(user=user)

    assert user.first_name == 'Adam'
    assert user.last_name == 'Nowak'
    assert user.email == 'adam@nowak.pl'
    assert profile.membership_number == '0000'
    assert profile.phone_number == '987654321'