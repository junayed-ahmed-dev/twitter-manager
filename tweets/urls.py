from django.urls import path
from . import views

urlpatterns = [

    path("dashboard/", views.dashboard, name="dashboard"),

    path("tweet/create/", views.compose),

    path("tweets/reply/<int:tweet_id>/", views.reply),

    path("tweets/retweet/<int:tweet_id>/", views.retweet),

    path("tweets/like/<int:tweet_id>/", views.like_tweet),

    path("tweets/search/", views.search_tweets),
    
    path("explore/", views.explore),

]