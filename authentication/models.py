from django.db import models
from django.contrib.auth.models import User


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    psrn = models.CharField(max_length=10, unique=True, default="")
    mess = models.CharField(max_length=10, default="")


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bits_id = models.CharField(max_length=13, default="")
    hostel = models.CharField(max_length=10, default="")
    mess = models.CharField(max_length=10, default="")
