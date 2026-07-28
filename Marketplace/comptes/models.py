from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('VENDOR', 'Vendor'),
        ('CUSTOMER', 'Customer')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )