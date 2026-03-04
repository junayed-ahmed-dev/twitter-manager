from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Follow, Profile
from tweets.models import Tweet
from django.shortcuts import get_object_or_404
from django.contrib import messages





def signup(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        age = request.POST["age"]

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.get_or_create(
            user=user,
            defaults={"age": age}
        )

        return redirect("/accounts/login/")

    return render(request, "signup.html")


@login_required
def search_users(request):

    query = request.GET.get("q")
    users = []

    if query:
        users = User.objects.filter(
            username__icontains=query
        )

    return render(request, "search_users.html", {
        "users": users,
        "query": query
    })



@login_required
def follow(request, user_id):

    user_to_follow = get_object_or_404(User, id=user_id)

    # Prevent following yourself
    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("/users/profile/" + str(user_id))

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    # If already following → unfollow
    if not created:
        follow.delete()

    return redirect("/users/profile/" + str(user_id))

@login_required
def followers(request):

    followers = Follow.objects.filter(
        following=request.user
    )

    return render(
        request,
        "followers.html",
        {"followers": followers}
    )


@login_required
def profile(request, user_id):

    user = User.objects.get(id=user_id)

    tweets = Tweet.objects.filter(
        author=user
    ).order_by("-created_at")

    followers = Follow.objects.filter(
        following=user
    ).count()

    following = Follow.objects.filter(
        follower=user
    ).count()

    # check if current user follows this profile
    is_following = Follow.objects.filter(
        follower=request.user,
        following=user
    ).exists()

    context = {
        "profile_user": user,
        "tweets": tweets,
        "followers": followers,
        "following": following,
        "is_following": is_following
    }

    return render(request, "profile.html", context)



@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        request.user.email = request.POST.get("email")
        age = request.POST.get("age")
        if age:
            profile.age = int(age)
        else:
            profile.age = None

        if "photo" in request.FILES:
            profile.photo = request.FILES["photo"]

        request.user.save()
        profile.save()

        return redirect("/users/profile/" + str(request.user.id))

    return render(request, "edit_profile.html", {
        "profile": profile
    })