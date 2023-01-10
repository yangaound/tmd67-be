from django.db import models
from django.contrib.auth.models import User

from tmd67_be.api.models import Club


class Product(models.Model):
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)


class Order(models.Model):
    user = models.ForeignKey(User, models.CASCADE)


class Item(models.Model):
    order = models.ForeignKey(Order, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    price = models.IntegerField(blank=True, null=True)


class Ticket(models.Model):
    item = models.ForeignKey(Item, models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    club = models.ForeignKey(Club, models.CASCADE, blank=True, null=True)
    email = models.CharField(max_length=60)
