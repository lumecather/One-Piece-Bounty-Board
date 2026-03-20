from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class PirateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bounty = models.IntegerField(default=0, help_text="Награда в белли")
    crew = models.CharField(max_length=100, blank=True, help_text="Пиратская команда")
    devil_fruit = models.CharField(max_length=100, blank=True, help_text="Дьявольский фрукт")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    class1 = models.CharField(max_length=100, blank=True, help_text="Класс")
    status = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.bounty} белл"

@receiver(post_save, sender=User)
def create_pirate_profile(sender, instance, created, **kwargs):
    if created:
        PirateProfile.objects.create(user=instance)
