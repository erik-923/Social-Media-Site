from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from django.urls import reverse
from .models import Post, Comment
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from users.models import FriendRequest



@login_required
def feed(request):
    user = request.user
    friends = user.profile.friends.all()
    posts = Post.objects.filter(Q(author__profile__in=friends) | Q(author=request.user)).order_by('-created_at')[:10]
    return render(request, "feed/feed.html", {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(reverse('feed'))
    else:
        form = PostForm()
    return render(request, "feed/create_post.html", {'form': form})

@login_required
def delete_post(request, id):
    post = Post.objects.filter(id=id).first()
    if post.author == request.user:
        post.delete()
        return HttpResponseRedirect(reverse('feed'))
    return HttpResponseForbidden("This is not your post.")
    

@login_required
def create_comment(request, id):
    post = Post.objects.get(id=id)
    if request.user.profile not in post.author.profile.friends.all() and request.user != post.author:
        return HttpResponseForbidden("You cannot comment on this post.")
    if request.method == 'POST': 
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.post = post
            form.instance.author = request.user
            form.save()
            return redirect(f'/post/{id}')
    else:
        form = CommentForm()
    return render(request, "feed/create_comment.html", {'form': form, 'post': post})

@login_required
def delete_comment(request, id):
    comment = Comment.objects.filter(id=id).first()
    if comment.author == request.user or comment.post.author == request.user:
        comment.delete()
        return HttpResponseRedirect(f'/post/{comment.post.id}')
    return HttpResponseForbidden("This is not your comment.")
    

@login_required
def post_details(request, id):
    post = Post.objects.get(id=id)
    if request.user.profile not in post.author.profile.friends.all() and request.user != post.author:
        return HttpResponseForbidden("You cannot view this post.")
    comments = post.comments.all().order_by('-created_at')[::-1]
    return render(request, "feed/post_details.html", {'comments': comments, 'post': post})

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user
    
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    
    post.save()
    count = post.like_count
    
    return JsonResponse({'like_count': count})

@login_required
def notifications(request):
    user = request.user
    friend_req = FriendRequest.objects.filter(to_user=user).order_by('-timestamp')
    user_posts = Post.objects.filter(author=user)
    comments = Comment.objects.filter(post__in=user_posts).exclude(author=user).order_by('-created_at')[:15]

    context = {
        'requests': friend_req,
        'comments': comments
    }
    return render(request, "feed/notifications.html", context)
