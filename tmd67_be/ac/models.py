from django.db import models
from django.contrib.auth.models import User
from django_fsm import FSMField

from tmd67_be.api.models import Club


class Ticket(models.Model):
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)


class Order(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    state = FSMField(default='draft')
    price = models.IntegerField(blank=True, null=True)


class Badge(models.Model):
    order = models.ForeignKey(Order, models.CASCADE)
    ticket = models.ForeignKey(Ticket, models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    club = models.ForeignKey(Club, models.CASCADE, blank=True, null=True)
