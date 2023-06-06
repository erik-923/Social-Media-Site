from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name = "feed"),
    path('post/create/', views.create_post, name = "create-post"),
    path('post/<int:id>/delete/', views.delete_post, name = "delete-post"),
    path('post/<int:id>/', views.post_details, name = "post-details"),
    path('post/<int:id>/comment/create/', views.create_comment, name = "create-comment"),
    path('comment/<int:id>/delete/', views.delete_comment, name = "delete-comment"),
    path('like/<int:post_id>/', views.like_post, name='like-post'),
    path('notifications', views.notifications, name='notifications')
]