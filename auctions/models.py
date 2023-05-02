from django.contrib.auth.models import AbstractUser, User
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    image = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=100)
    title = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)

class Bid(models.Model):
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Comment(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
