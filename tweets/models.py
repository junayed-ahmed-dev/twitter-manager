from django.db import models
from django.contrib.auth.models import User


class Tweet(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    retweet_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="retweets"
    )


class Like(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    class Meta:
        unique_together = ("user", "tweet")