import pytest
from rentals.models import Category, Equipment



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