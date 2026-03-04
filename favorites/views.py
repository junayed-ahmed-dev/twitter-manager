from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FavoriteList, FavoriteItem
from tweets.models import Tweet


@login_required
def favorite_lists(request):

    lists = FavoriteList.objects.filter(user=request.user)

    return render(
        request,
        "favorites.html",
        {"lists": lists}
    )


@login_required
def create_list(request):

    if request.method == "POST":

        name = request.POST["name"]

        FavoriteList.objects.create(
            user=request.user,
            name=name
        )

    return redirect("/favorites/")


@login_required
def add_to_list(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    lists = FavoriteList.objects.filter(user=request.user)

    if request.method == "POST":

        list_id = request.POST["list"]

        fav_list = get_object_or_404(
            FavoriteList,
            id=list_id,
            user=request.user
        )

        FavoriteItem.objects.get_or_create(
            list=fav_list,
            tweet=tweet
        )

        return redirect("/favorites/")

    return render(
        request,
        "favorites.html",
        {
            "lists": lists,
            "tweet": tweet
        }
    )


@login_required
def view_list(request, list_id):

    fav_list = get_object_or_404(
        FavoriteList,
        id=list_id,
        user=request.user
    )

    items = FavoriteItem.objects.filter(list=fav_list)

    return render(
        request,
        "favorite_list.html",
        {
            "list": fav_list,
            "items": items
        }
    )