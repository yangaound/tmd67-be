from django.contrib.auth.models import User
from django.db import models
from django_fsm import FSMField


class TicketProduct(models.Model):
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"TicketProduct<id={self.id}, name={self.english_name}>"


class Order(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    state = FSMField(default="unpaid")
    amount = models.IntegerField(default=0)
    created_time = models.DateTimeField(
        auto_now_add=True, null=True, blank=True
    )
    updated_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    product_items = models.ManyToOneRel(
        "ac.OrderItem", models.CASCADE, field_name="product_items"
    )

    def __str__(self):
        return f"Order<id={self.id}, created_time={self.created_time}>"


class Ticket(models.Model):
    order = models.ForeignKey(Order, models.CASCADE)
    ticket_product = models.ForeignKey(TicketProduct, models.CASCADE)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    club = models.ForeignKey("api.Club", models.CASCADE, blank=True, null=True)


class ProductItem(models.Model):
    order = models.ForeignKey(
        Order, models.CASCADE, related_name="product_items", null=True
    )
    ticket_product = models.ForeignKey(TicketProduct, models.CASCADE)
    quantity = models.IntegerField(0)


class PaymentRecord(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    merchant_id = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
