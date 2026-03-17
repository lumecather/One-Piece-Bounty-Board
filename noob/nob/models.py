from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)  # заголовок
    content = models.TextField()  # текст поста
    date = models.DateTimeField(auto_now_add=True)  # дата создания
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    bounty = models.IntegerField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)  # имя комментирующего
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="comments/", blank=True, null=True)

    def __str__(self):
        return f'Комментарий от {self.author} к {self.post}'
