from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_welcome_email(user_email, username):
    """Отправляет приветственное письмо новому пирату"""
    time.sleep(5)  # Имитируем долгую задачу
    send_mail(
        subject='Добро пожаловать на борт! 🏴‍☠️',
        message=f'Привет, {username}! Ты стал пиратом. Лови свою первую награду — 100 белл!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return f'Письмо отправлено {user_email}'


@shared_task
def increase_bounties():
    """
    Повышает награду пиратам, которых не поймали за неделю
    Запускать каждое воскресенье в 9:00
    """
    from .models import Post

    week_ago = timezone.now() - timedelta(days=7)
    old_posts = Post.objects.filter(date__lte=week_ago)

    updated_count = 0
    for post in old_posts:
        post.bounty = int(post.bounty * 1.1)
        post.save()
        updated_count += 1

    return f'Повышена награда для {updated_count} пиратов'