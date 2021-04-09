from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts")
    content = models.TextField()
    likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name.username} posted on " + self.timestamp.strftime("%b %d %Y, %I:%M %p");

class Like(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")

    def __str__(self):
        return f"{self.name.username} liked {self.post.content}"
