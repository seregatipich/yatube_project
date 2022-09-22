from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Group, Post, User


user = User()


def index(request):
    posts: Post = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'page_title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/group_list.html', {
        'group': group, 'posts': posts, 'page_obj': page_obj})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    paginator = Paginator(author.posts.all(), settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts': author.posts.all(),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
            .select_related('author')
            .select_related('group'), id=post_id)
    context = {
        'post': post,
        'id': post_id,
        'page_title': post.text[:30],
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    """Модуль отвечающий за страницу редактирования текста постов."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
        'id': post_id
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method != 'POST':
        return render(request, 'posts/post_create.html', context)
    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.author = request.user
    post.save()
    return redirect('posts:post_detail', post_id)
