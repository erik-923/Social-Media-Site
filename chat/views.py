from django.shortcuts import render, redirect, get_object_or_404
from .models import Chat, Message
from django.contrib.auth.models import User
from .forms import ChatForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import models
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseForbidden




# Create your views here.
@login_required
def chat_list(request):
    chats = request.user.chats.annotate(
        most_recent_message_timestamp=models.Max('messages__timestamp')
        ).order_by('-most_recent_message_timestamp')

    return render(request, "chat/chat_list.html", {'chats': chats})

@login_required
def direct_message(request, id):
    user = User.objects.filter(id=id).first()
    users = [user, request.user]
    chats = Chat.objects.filter(participants__in=users)
    for chat in chats:
        if chat.participants.count() == len(users):
            if set(chat.participants.all()) == set(users):
                return redirect('chat-view', chat.id)

    chat = Chat.objects.create()
    chat.participants.add(request.user, user)

    return redirect('chat-view', chat.id)

@login_required
def chat_create(request):
    form = ChatForm(request.POST or None, request=request)
    friends = request.user.profile.friends.all()
    if request.method == 'POST':
        if form.is_valid():
            recipients = form.cleaned_data['recipients']
            parts = list(recipients)
            parts.append(request.user)
            user = request.user
            
            chats = Chat.objects.filter(participants__in=recipients)
            for chat in chats:
                if chat.participants.count() == len(parts):
                    if set(chat.participants.all()) == set(parts):
                        return redirect('chat-view', chat.id)

            # Create a new chat if it doesn't exist
            chat = Chat.objects.create()
            chat.participants.add(user, *recipients)

            # Redirect to the new chat room
            return redirect('chat-view', id=chat.id)

    context = {
        'form': form
    }

    return render(request, 'chat/chat_create.html', context)

@login_required
def chat_view(request, id):
    chat = get_object_or_404(Chat, id=id)
    messages = chat.messages.all().order_by('-timestamp')[:50][::-1]
    participants = chat.participants.all().exclude(id=request.user.id)
    
    if request.user not in chat.participants.all():
        return HttpResponseForbidden("You are not a participant of this chat.")
    if request.method == 'POST':
        message = request.POST.get('message')
        sender = request.user
        Message.objects.create(chat=chat, sender=sender, message=message)
        return redirect('chat-view', id=id)  # Perform a redirect after form submission
    

    
    context = {
        'chat': chat,
        'messages': messages,
        'participants': participants
    }
    return render(request, 'chat/chat_view.html', context)


@login_required
def delete_message(request, id):
    message = get_object_or_404(Message, id=id)
    if message.sender == request.user:
        message.delete()
        return redirect('chat-view', message.chat.id)
    return HttpResponseForbidden("This is not your message.")
    
    

@login_required
def leave_chat(request, id):
    chat = get_object_or_404(Chat, id=id)
    chat.remove_participant(request.user)
    if chat.participants.count() <= 1:
        chat.delete()
    return redirect('chat-list')


