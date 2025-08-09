import pytest
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from rentals.models import Category, Equipment, Cart, CartItem, Rental, RentalItem, UserProfile



@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='passwordtest',
        first_name='Jan',
        last_name='Kowalski',
        email='jan@kowalski.pl'
    )


@pytest.fixture
def user_profile(db, user):
    return UserProfile.objects.create(
        user=user,
        membership_number='9999',
        phone_number='123456789',
    )


@pytest.fixture
def client_auth(client, user):
    client.login(username='testuser', password='passwordtest')
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(name='Skaly')


@pytest.fixture
def equipment1(category):
    return Equipment.objects.create(
        name='Ekspres',
        category=category,
        description='Ekspres 15cm firmy Simond',
        quantity=10,
        price_per_day=Decimal('4.00'),
        deposit=Decimal('30.00'),
    )


@pytest.fixture
def equipment2(category):
    return Equipment.objects.create(
        name='Crashpad',
        category=category,
        description='Crashpad firmy Ocun',
        quantity=5,
        price_per_day=Decimal('12.00'),
        deposit=Decimal('100.00'),
    )


@pytest.fixture
def cart(user):
    return Cart.objects.create(
        user=user,
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 7),
        is_active=True,
    )


@pytest.fixture
def rental(user):
    return Rental.objects.create(
        user=user,
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 15),
        status='pending',
    )


@pytest.fixture
def rental_with_item(rental, equipment1):
    RentalItem.objects.create(
        rental=rental,
        equipment=equipment1,
        quantity=2,
    )
    return rental