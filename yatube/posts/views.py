from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    template = '/templates/posts/index.html'
    return render(request, template) 

def group_posts(request, slug):
    return HttpResponse(f'Hi {slug}')
