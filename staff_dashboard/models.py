from django.db import models
import uuid


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    breakfast = models.JSONField()
    lunch = models.JSONField()
    dinner = models.JSONField()


class FoodRating(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    item = models.CharField(max_length=255)
    ratings = models.CharField(max_length=255, blank=True)

    def add_rating(self, rating):
        if self.ratings:
            self.ratings += f",{rating}"
        else:
            self.ratings = rating

    def get_ratings_list(self):
        return [int(r) for r in self.ratings.split(",")] if self.ratings else []

    class Meta:
        unique_together = ("menu", "item")
