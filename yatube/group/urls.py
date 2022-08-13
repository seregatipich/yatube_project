from django.urls import path
from . import views

urlpatterns = [
    path('', group_posts())
]