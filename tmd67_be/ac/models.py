from django.contrib.auth.models import User
from django.db import models
from django_fsm import FSMField

from tmd67_be.api.models import Club


class Ticket(models.Model):
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Ticket<id={self.id}, name={self.english_name}>"


class Order(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    state = FSMField(default="unpaid")
    amount = models.IntegerField(default=0)
    created_time = models.DateTimeField(
        auto_now_add=True, null=True, blank=True
    )


class Badge(models.Model):
    order = models.ForeignKey(Order, models.CASCADE)
    ticket = models.ForeignKey(Ticket, models.CASCADE)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    club = models.ForeignKey(Club, models.CASCADE, blank=True, null=True)
