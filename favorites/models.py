from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


class FavoriteList(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)


class FavoriteItem(models.Model):

    list = models.ForeignKey(
        FavoriteList,
        on_delete=models.CASCADE
    )

    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("list", "tweet")