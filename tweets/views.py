from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tweet, Like
from users.models import Follow
from django.db.models import Q


@login_required
def explore(request):

    tweets = Tweet.objects.all().order_by("-created_at")

    return render(request, "explore.html", {
        "tweets": tweets
    })


@login_required
def dashboard(request):

    following = Follow.objects.filter(
        follower=request.user
    ).values_list("following", flat=True)

    tweets = Tweet.objects.filter(
        author__in=list(following) + [request.user.id]
    ).order_by("-created_at")

    return render(request, "dashboard.html", {
        "tweets": tweets
    })


@login_required
def compose(request):

    if request.method == "POST":

        content = request.POST.get("content")

        Tweet.objects.create(
            author=request.user,
            content=content
        )

        return redirect("dashboard")

    return render(request, "compose.html")


@login_required
def reply(request, tweet_id):

    parent = get_object_or_404(Tweet, id=tweet_id)

    if request.method == "POST":

        Tweet.objects.create(
            author=request.user,
            content=request.POST.get("content"),
            reply_to=parent
        )

        return redirect("dashboard")

    return render(request, "reply.html", {
        "tweet": parent
    })


@login_required
def retweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    Tweet.objects.create(
        author=request.user,
        retweet_of=tweet
    )

    return redirect("dashboard")


@login_required
def like_tweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    Like.objects.get_or_create(
        user=request.user,
        tweet=tweet
    )

    return redirect("dashboard")


@login_required
def search_tweets(request):

    query = request.GET.get("q")
    tweets = []

    if query:
        tweets = Tweet.objects.filter(
            Q(content__icontains=query)
        ).order_by("-created_at")

    return render(request, "search_tweets.html", {
        "tweets": tweets,
        "query": query
    })


def welcome(request):
    return render(request, "welcome.html")