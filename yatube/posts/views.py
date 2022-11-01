from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .forms import PostForm

from .models import Group, Post, User


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    post_count = author.posts.count()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'post_count': post_count,
        'page_obj': page_obj,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:settings.SLICE_END]
    author = post.author
    post_count = author.posts.count()
    context = {
        'post': post,
        'post_title': post_title,
        'author': author,
        'post_count': post_count,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(f"/profile/{post.author}/", {"form": form})
    form = PostForm()
    groups = Group.objects.all()
    context = {"form": form, "groups": groups}
    return render(request, 'posts/create_post.html', context)
