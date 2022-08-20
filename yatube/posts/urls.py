from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index),
    path('group/', views.index, name='group_posts')
]
