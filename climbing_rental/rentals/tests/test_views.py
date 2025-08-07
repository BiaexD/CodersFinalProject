import pytest
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse
from rentals.models import Category, Equipment, Cart, CartItem, Rental, RentalItem, UserProfile


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
def test_category_detail_shows_only_available_equipment(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Zima")
    eq1 = Equipment.objects.create(
        name="Raki Petzl",
        category=category,
        quantity=5,
        price_per_day=10.0,
        deposit=100.0,
    )
    eq2 = Equipment.objects.create(
        name="Czekan Black Diamond",
        category=category,
        quantity=2,
        price_per_day=15.0,
        deposit=120.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-10-01",
        end_date="2025-10-07",
        is_active=True
    )

    other_user = User.objects.create_user(username="inna_osoba", password="haslo123")
    other_cart = Cart.objects.create(
        user=other_user,
        start_date="2025-10-01",
        end_date="2025-10-07",
        is_active=True
    )

    CartItem.objects.create(cart=other_cart, equipment=eq2, quantity=2)

    url = reverse('category_detail', args=[category.pk])
    response = client.get(url)
    content = response.content.decode()

    assert "Raki Petzl" in content
    assert "Czekan Black Diamond" not in content



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
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment1 = Equipment.objects.create(
        name="Ekspres",
        category=category,
        quantity=10,
        price_per_day=4.00,
        deposit=30.0
    )
    equipment2 = Equipment.objects.create(
        name="Crashpad",
        category=category,
        quantity=5,
        price_per_day=12.00,
        deposit=100.0
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-10-01",
        end_date="2025-10-07",
        is_active=True
    )

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
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Ekspres" in content
    assert "Crashpad" in content
    assert "2" in content
    assert "1" in content
    assert "20.0" in content or "20.00" in content
    assert "160.0" in content or "160.00" in content



@pytest.mark.django_db
def test_add_to_cart_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-10",
        is_active=True,
    )

    url = reverse("add_to_cart", args=[equipment.pk])
    for i in range(5):
        response = client.post(url)
        assert response.status_code == 302

    cart_item = CartItem.objects.get(cart=cart, equipment=equipment)
    assert cart_item.quantity == 5

    response = client.post(url)
    assert response.status_code == 302
    cart_item.refresh_from_db()
    assert cart_item.quantity == 5
    messages = list(response.wsgi_request._messages)
    assert any("nie mozna dodac wiecej" in str(m).lower() for m in messages)



@pytest.mark.django_db
def test_remove_from_cart_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-10",
        is_active=True,
    )

    cart_item = CartItem.objects.create(cart=cart, equipment=equipment, quantity=2)
    url = reverse("remove_from_cart", args=[equipment.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not CartItem.objects.filter(cart=cart, equipment=equipment).exists()



@pytest.mark.django_db
def test_increase_quantity_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-10",
        is_active=True,
    )

    cart_item = CartItem.objects.create(cart=cart, equipment=equipment, quantity=4)
    url = reverse("increase_quantity", args=[equipment.pk])

    response = client.post(url)
    cart_item.refresh_from_db()
    assert cart_item.quantity == 5

    response = client.post(url)
    cart_item.refresh_from_db()
    assert cart_item.quantity == 5
    messages = list(response.wsgi_request._messages)
    assert any("nie mamy więcej" in str(m).lower() for m in messages)



@pytest.mark.django_db
def test_decrease_quantity_adn_remove_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-10",
        is_active=True,
    )

    cart_item = CartItem.objects.create(cart=cart, equipment=equipment, quantity=2)
    url = reverse("decrease_quantity", args=[equipment.pk])

    response = client.post(url)
    cart_item.refresh_from_db()
    assert cart_item.quantity == 1

    response = client.post(url)
    assert not CartItem.objects.filter(cart=cart, equipment=equipment).exists()



@pytest.mark.django_db
def test_select_dates_desactivates_previous_cart(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')

    old_cart = Cart.objects.create(
        user=user,
        start_date="2025-08-10",
        end_date="2025-08-15",
        is_active=True,
    )

    url = reverse('select_dates')
    response = client.post(url, {
        'start_date': '2025-09-01',
        'end_date': '2025-09-05',
    })

    old_cart.refresh_from_db()
    assert old_cart.is_active == False

    new_cart = Cart.objects.get(user=user, is_active=True)
    assert str(new_cart.start_date) == "2025-09-01"
    assert str(new_cart.end_date) == "2025-09-05"
    assert response.status_code == 302



def test_user_rentals_view(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')
    Rental.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-15",
        status="pending",
    )

    url = reverse('user_rentals')
    response = client.get(url)
    assert response.status_code == 200
    assert "2025-08-01" in response.content.decode()



def test_order_summary_view(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')
    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    cart = Cart.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-15",
        is_active=True,
    )

    CartItem.objects.create(
        cart=cart,
        equipment=equipment,
        quantity=2
    )

    url = reverse('order_summary')
    response = client.get(url)
    assert response.status_code == 200
    assert "Ekspres" in response.content.decode()

    response = client.post(url)
    assert response.status_code == 302

    cart.refresh_from_db()
    assert cart.is_active is False



@pytest.mark.django_db
def test_finish_rental_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')
    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )

    rental = Rental.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-15",
        status="pending",
    )

    RentalItem.objects.create(
        rental=rental,
        equipment=equipment,
        quantity=2
    )

    equipment.quantity -= 2
    equipment.save()

    url = reverse('finish_rental', args=[equipment.pk])
    response = client.get(url)
    assert response.status_code == 302

    rental.refresh_from_db()
    assert rental.status == "finished"

    equipment.refresh_from_db()
    assert equipment.quantity == 5

    messages = list(response.wsgi_request._messages)
    assert any("zostalo zakonczone" in str(m) for m in messages)



@pytest.mark.django_db
def test_rental_detail_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest')
    client.login(username='testuser', password='passwordtest')
    category = Category.objects.create(name="Skaly")
    equipment = Equipment.objects.create(
        name="Ekspres",
        category=category,
        description="Ekspres 15 cm firmy Simond",
        quantity=5,
        price_per_day=2.0,
        deposit=30.0,
    )
    rental = Rental.objects.create(
        user=user,
        start_date="2025-08-01",
        end_date="2025-08-15",
        status="pending",
    )
    RentalItem.objects.create(
        rental=rental,
        equipment=equipment,
        quantity=2
    )

    url = reverse('rental_detail', args=[rental.pk])
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Ekspres" in content
    assert "2025-08-01" in content
    assert "ilosc: 2" in content



@pytest.mark.django_db
def test_user_data_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest', first_name='Jan', last_name='Kowalski', email='jan@kowalski.pl')
    UserProfile.objects.create(user=user, membership_number='9999', phone_number='123456789')
    client.login(username='testuser', password='passwordtest')

    url = reverse('user_data')
    response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "Jan" in content
    assert "Kowalski" in content
    assert "jan@kowalski.pl" in content
    assert "9999" in content
    assert "123456789" in content
    assert "Edytuj" in content



@pytest.mark.django_db
def test_user_edit_data_view(client):
    user = User.objects.create_user(username='testuser', password='passwordtest', first_name='Jan', last_name='Kowalski', email='jan@kowalski.pl')
    UserProfile.objects.create(user=user, membership_number='9999', phone_number='123456789')
    client.login(username='testuser', password='passwordtest')

    new_data = {
        'first_name': 'Adam',
        'last_name': 'Nowak',
        'email': 'adam@nowak.pl',
        'membership_number': '0000',
        'phone_number': '987654321',
    }

    url = reverse('user_edit_data')
    response = client.post(url, {
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