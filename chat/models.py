from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    
    def remove_participant(self, user):
        self.participants.remove(user)
        if self.participants.count() == 0:
            self.delete()
    
    def get_most_recent_message(self):
        return self.messages.order_by('-timestamp').first()

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
