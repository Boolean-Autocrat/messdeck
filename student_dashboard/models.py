from django.db import models
from django.contrib.auth.models import User
import uuid


class Complaints(models.Model):
    complaint_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint_description = models.CharField(max_length=200)
    complaint_status = models.CharField(max_length=20, default="Pending")
    complaint_date = models.DateField(auto_now_add=True)
    no_of_files = models.IntegerField(default=0)


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal = models.CharField(max_length=10)  # 'Breakfast', 'Lunch', 'Dinner'
    date = models.DateField()
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "meal", "date"]
