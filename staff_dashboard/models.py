from django.db import models
import uuid
from django.contrib.auth.models import User


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)

    @property
    def items(self):
        return Food.objects.filter(menu=self)


class Food(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    meal = models.CharField(max_length=255)
    item = models.CharField(max_length=255)


class FoodRating(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=255)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.item, self.rating, self.user

    class Meta:
        unique_together = ("menu", "item")
