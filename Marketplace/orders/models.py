from django.db import models

from django.conf import settings
from products.models import Product

# Create your models here.
from django.db import models
from django.conf import settings


class Order(models.Model):

    STATUS = (
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )    