from django.db import models


# Create your models here.
class Review(models.Model):

    product = models.ForeignKey(
        'products.Product',
        related_name='reviews',
        on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)