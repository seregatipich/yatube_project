from django.urls import path
from . import views

urlpatterns = [
    path('group/<slug:pk>/', views.group_posts),
    path('', views.index)
]