from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group': group, 
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    count = post_list.count()
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {
        'author': user, 'page_obj': page_obj, 'count': count})


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    count_post = post.author.posts.count()
    return render(request, template, {
        'post': post, 'count_post': count_post})
