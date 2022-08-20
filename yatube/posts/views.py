from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import render
from .models import Post


def index(request):
    post = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts':posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    return HttpResponse(f'Hi {slug}')
