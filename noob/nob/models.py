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


class PostBountyAuto(models.Model):
    post = models.OneToOneField('Post', on_delete=models.CASCADE, related_name='bounty_auto')
    enabled = models.BooleanField(default=False)
    percent = models.IntegerField(default=5, help_text="На сколько % поднимать баунти")
    interval_days = models.IntegerField(default=7, help_text="Как часто поднимать (дни)")
    last_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.post.title} - {'Вкл' if self.enabled else 'Выкл'}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="comments/", blank=True, null=True)

    def __str__(self):
        return f'Комментарий от {self.author} к {self.post}'


class PirateProfile(models.Model):
    class Role(models.TextChoices):
        USERR = "just_user", "Пользователь"
        PIRATE = 'pirate', 'Пират'
        HUNTER = 'hunter', 'Охотник за головами'
        ADMIN = 'admin', 'Администратор'
        OFFICIAL = 'official', 'Сотрудник организации'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USERR)
    organization = models.CharField(max_length=100, blank=True, help_text='Название организации (если есть)')

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"


@receiver(post_save, sender=User)
def create_pirate_profile(sender, instance, created, **kwargs):
    if created:
        PirateProfile.objects.create(user=instance)
