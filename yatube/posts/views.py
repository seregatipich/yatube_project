from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


user = User()


def paginator(request, queryset):
    page = Paginator(queryset, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    return page.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    template = 'posts/index.html'
    context = {'page_obj': page_obj,}
    return render(request, template, context)


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
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts': author.posts.all(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
            .select_related('author')
            .select_related('group'), id=post_id)
    following = False
    if request.user.is_authenticated:
        following = post.author.following.filter(user=request.user).exists()
    form = CommentForm()
    comments_list = post.comments.all()
    comments_obj = comments_list
    context = {
        'post': post,
        'id': post_id,
        'page_obj': comments_obj,
        'page_title': post.text[:30],
        'form': form,
        'following': following,
        'author': post.author
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
    post = get_object_or_404(Post, id=post_id)
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    template = 'posts/post_create.html'
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
        'id': post_id
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginator(request, posts)
    template = 'posts/follow.html'
    context = {'page_obj': page_obj, }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
        return redirect('posts:profile', username=username)
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    if Follow.objects.filter(user=user, author__username=username).exists():
        get_object_or_404(Follow, user=user,
                          author__username=username).delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:index')
