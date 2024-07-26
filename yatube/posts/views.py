from .forms import PostForm, CommentForm
from .models import Post, Group, Follow
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from yatube.settings import QTY_POSTS_PAGE

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, QTY_POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, QTY_POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CommentForm()
    context = {
        'post': post,
        'can_edit': post.author == request.user,
        'comments': post.comments.all(),
        'form': comment_form,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    profile_obj = get_object_or_404(User, username=username)
    post_list = profile_obj.posts.all()
    paginator = Paginator(post_list, QTY_POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if not request.user.is_anonymous:
        following = Follow.objects.filter(
            user=request.user,
            author=profile_obj,
        ).exists()
    context = {
        'profile': profile_obj,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        model = form.save(commit=False)
        model.author = request.user
        model.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, instance=post,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
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
    template = 'posts/follow.html'
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    paginator = Paginator(post_list, QTY_POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=author,
    ).delete()
    return redirect('posts:profile', username=username)
