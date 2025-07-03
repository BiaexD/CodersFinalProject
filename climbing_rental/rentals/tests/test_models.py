import pytest
from django.contrib.auth.models import User
from rentals.models import Category, Equipment, Rental, RentalItem



@pytest.mark.django_db
def test_create_category():
    category = Category.objects.create(
        name = "Liny",
        description = ""
    )
    assert category.name == "Liny"
    assert category.description == ""



@pytest.mark.django_db
def test_create_equipment():
    category = Category.objects.create(name="Liny")
    equipment = Equipment.objects.create(
        name = "Lina Beal",
        category = category,
        description = "single rope, 60m",
        quantity = 5,
        price_per_day = 6.00,
        deposit = 100.00
    )
    assert equipment.name == "Lina Beal"
    assert equipment.category == category
    assert equipment.description == "single rope, 60m"
    assert equipment.quantity == 5
    assert equipment.price_per_day == 6.00
    assert equipment.deposit == 100.00



@pytest.mark.django_db
def test_create_rental():
    user = User.objects.create_user(username = "testuser", password = "testpass")
    rental = Rental.objects.create(
        user = user,
        start_date = '2025-06-01',
        end_date = '2025-06-06',
        created_at = '2025-05-26',
    )
    assert rental.user.username == "testuser"
    assert rental.start_date == "2025-06-01"
    assert rental.end_date == '2025-06-06'
    assert rental.status == 'pending'
    assert rental.created_at is not None



@pytest.mark.django_db
def test_create_rental_item():
    category = Category.objects.create(name="Liny")
    equipment = Equipment.objects.create(
        name = "Lina Beal",
        category = category,
        quantity = 5,
        price_per_day = 6.00,
        deposit = 100.00
    )
    user = User.objects.create_user(username = "testuser", password = "testpass")
    rental = Rental.objects.create(
        user = user,
        start_date = '2025-06-01',
        end_date = '2025-06-06',
    )
    item = RentalItem.objects.create(
        rental = rental,
        equipment = equipment,
        quantity = 1,
    )
    assert item.rental == rental
    assert item.equipment == equipment
    assert item.quantity == 1