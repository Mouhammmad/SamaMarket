from django.db import models

# Create your models here.
from accounts.models import User


class Shop(models.Model):

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shop'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    city = models.CharField(max_length=100)

    followers = models.ManyToManyField(
        User,
        blank=True,
        related_name='following'
    )

    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name