# Create your models here.
from django.db import models


class User(models.Model):
    account = models.CharField(max_length=255)
    password=models.CharField(max_length=255, default="")
    record = models.TextField(default="")

