from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    bounty = models.BigIntegerField(default=0,
                                    validators=[MinValueValidator(0), MaxValueValidator(10_000_000_000)])
    organization = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['author']),
            models.Index(fields=['organization']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                img.thumbnail((600, 600))
                img.save(self.image.path)


class PostBountyAuto(models.Model):
    post = models.OneToOneField('Post', on_delete=models.CASCADE, related_name='bounty_auto')
    enabled = models.BooleanField(default=False)
    percent = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(500)],
    )
    interval_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
    )
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                img.thumbnail((600, 600))
                img.save(self.image.path)


class PirateProfile(models.Model):
    class Role(models.TextChoices):
        USERR = "just_user", "User"
        PIRATE = 'pirate', 'Pirate'
        HUNTER = 'hunter', 'Bounty hunter'
        ADMIN = 'admin', 'Admin'
        OFFICIAL = 'official', 'Official'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USERR)
    organization = models.CharField(max_length=100, blank=True, help_text='Name of organization (if exist)')

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                img.thumbnail((600, 600))
                img.save(self.image.path)
