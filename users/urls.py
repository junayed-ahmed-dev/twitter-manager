from django.urls import path
from . import views

urlpatterns = [

    path("signup/", views.signup),

    path("search/", views.search_users),

    path("profile/<int:user_id>/", views.profile),

    path("follow/<int:user_id>/", views.follow),

    path("followers/", views.followers),

    path("edit/", views.edit_profile),

]