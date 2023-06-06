from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat-list'),
    path('create/', views.chat_create, name='create-chat'),
    path('<int:id>/', views.chat_view, name='chat-view'),
    path('message/<int:id>/delete/', views.delete_message, name='delete-message'),
    path('<int:id>/leave/', views.leave_chat, name='leave-chat'),
    path('direct_message/<int:id>/', views.direct_message, name='direct-message')
    ]