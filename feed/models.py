from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose, Thumbnail


# Create your models here.


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to = "post_pics")
    caption = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    picture = ImageSpecField(
        source='image',
        processors=[
        Transpose(),
        Thumbnail(width=300, height=300, crop=True)],
        format='JPEG',
        options={'quality': 90})
    like_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Post object first to assign an id
        self.like_count = self.likes.count()  # Update the like_count based on the likes relationship
        super().save(*args, **kwargs)  # Save the updated like_count

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
