from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from .models import Profile, FriendRequest
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import random
from django.urls import reverse
from django.db.models import Q
from feed.models import Post

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now login!')
            return redirect(reverse('login'))
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def my_profile(request):
    profile = request.user.profile
    you = profile.user
    sent_friend_requests = FriendRequest.objects.filter(from_user=you)
    rec_friend_requests = FriendRequest.objects.filter(to_user=you)
    user_posts = [] #Post.objects.filter(user_name=you)
    friends = profile.friends.all()
    button_status = 'none'
    if profile not in request.user.profile.friends.all():
        button_status = 'not_friend'

		# if we have sent him a friend request
        if len(FriendRequest.objects.filter(
			from_user=request.user).filter(to_user=you)) == 1:
            button_status = 'friend_request_sent'

        if len(FriendRequest.objects.filter(
			from_user=profile.user).filter(to_user=request.user)) == 1:
            button_status = 'friend_request_received'

    posts = Post.objects.filter(author=you).order_by('-created_at')[:18]

    context = {
		'u': you,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
		'post_count': user_posts.count,
        'posts': posts
    }
    return render(request, "users/profile.html", context)

@ login_required
def edit_profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('my-profile')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)
	context ={
		'u_form': u_form,
		'p_form': p_form,
	}
	return render(request, 'users/edit_profile.html', context)

@login_required
def profile_view(request, slug):
    profile = Profile.objects.filter(slug=slug).first()
    u = profile.user
    sent_friend_requests = FriendRequest.objects.filter(from_user=profile.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=profile.user)
    user_posts = [] #Post.objects.filter(user_name=u)

    friends = profile.friends.all()

	# is this user our friend
    button_status = 'none'
    if profile not in request.user.profile.friends.all():
        button_status = 'not_friend'

		# if we have sent him a friend request
        if len(FriendRequest.objects.filter(
            from_user=request.user).filter(to_user=profile.user)) == 1:
                button_status = 'friend_request_sent'

		# if we have recieved a friend request
        if len(FriendRequest.objects.filter(
            from_user=profile.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'
    
    posts = Post.objects.filter(author=u).order_by('-created_at')[:18]

    context = {
		'u': u,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
		'post_count': user_posts.count,
        'posts': posts
	}
    return render(request, "users/profile.html", context)

@login_required
def send_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	FriendRequest.objects.get_or_create(
			from_user=request.user,
			to_user=user)
	return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def cancel_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(
			from_user=request.user,
			to_user=user).first()
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def accept_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	user1 = frequest.to_user
	user2 = from_user
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	if(FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()):
		request_rev = FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()
		request_rev.delete()
	frequest.delete()
	return HttpResponseRedirect(f'/users/{request.user.profile.slug}')

@login_required
def delete_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.slug))

@login_required
def delete_friend(request, id):
	user_profile = request.user.profile
	friend_profile = get_object_or_404(User, id=id).profile
	user_profile.friends.remove(friend_profile)
	friend_profile.friends.remove(user_profile)
	return HttpResponseRedirect('/users/{}'.format(friend_profile.slug))

@login_required
def search_users(request):
    query = request.GET.get('q')
    users = None

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    context = {'users': users}
    return render(request, 'users/search_users.html', context)

def friend_recomendations(request):
	# gets all profiles excluding self
    users = Profile.objects.exclude(user=request.user)
	# gets all users sent friend requests
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    sent_to = []
    friends = []


	# loops through all users except self
    for user in users:
		# gets all of users friends
        friend = user.friends.all()
        for f in friend:
			# if the user is already in the friends list remove them from the query
            if f in friends:
                friend = friend.exclude(user=f.user)
			# add all of the remaining recomended friends to the friends list
        friends+=friend
	
    for i in sent_to:
        if i in friends:
            friends.remove(i)
	# gets all of self's friends and loops through them
    my_friends = request.user.profile.friends.all()
    for i in my_friends:
		# if self is already friends with the user remove them from recomended friends list
        if i in friends:
            friends.remove(i)
	# if self is in the recomended friends list remove them
    if request.user.profile in friends:
        friends.remove(request.user.profile)
	# takes a random sample of the users of the minimum of either the number of users or 10
    random_list = random.sample(list(users), min(len(list(users)), 10))
	
	# loops through the sample and removes users if they are already in friends list
    for r in random_list:
        if r in friends:
            random_list.remove(r)
	# adds remaining random sample to the friends list
    friends+=random_list
	# loops through self's friends and if they are in the friend rec list, remove them
    for i in my_friends:
        if i in friends:
            friends.remove(i)

    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    
    for i in sent_to:
         if i.profile in friends:
              friends.remove(i.profile)

        
    context = {
		'users': friends,
		'sent': sent_to
	}
	# renders and html page that takes the friend rec list and the list of sent friend requests
    return render(request, "users/friend_recomendations.html", context)

def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context={
	'friends': friends
	}
    return render(request, "users/friend_list.html", context)