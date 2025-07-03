from django.db import models



class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



class Equipment(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=5, decimal_places=2)
    deposit = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name