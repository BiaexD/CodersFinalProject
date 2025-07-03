import pytest
from rentals.models import Category

@pytest.mark.django_db
def test_create_category():
    category = Category.objects.create(
        name = "Liny",
        description = ""
    )
    assert category.name == "Liny"
    assert category.description == ""

