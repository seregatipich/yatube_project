from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Group, Post, User
from .forms import PostForm
user = User()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/group_list.html', {
        'group': group, 'posts': posts, 'page_obj': page_obj})


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
    is_form_edit = True
    post = get_object_or_404(Post, pk__iexact=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or None,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)
        return render(request, 'posts/post_create.html', {
            'form': form, 'is_form_edit': is_form_edit, 'post': post})
    else:
        return redirect('posts:post_detail', post_id)
