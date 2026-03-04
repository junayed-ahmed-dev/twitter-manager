from django.urls import path
from . import views

urlpatterns = [

    path("", views.favorite_lists),

    path("create/", views.create_list),

    path("add/<int:tweet_id>/", views.add_to_list),
    path("list/<int:list_id>/", views.view_list),

]