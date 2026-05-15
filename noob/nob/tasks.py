from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_welcome_email(user_email, username):
    """Отправляет приветственное письмо новому пирату"""
    time.sleep(5)
    send_mail(
        subject='Добро пожаловать на борт! 🏴‍☠️',
        message=f'Привет, {username}! Ты стал пиратом. Лови свою первую награду — 100 белл!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    return f'Письмо отправлено {user_email}'


@shared_task
def increase_single_post_bounty(post_id):
    """
    Поднимает баунти у конкретного поста по его индивидуальным настройкам
    """
    from .models import Post, PostBountyAuto

    try:
        auto = PostBountyAuto.objects.get(post_id=post_id)

        if not auto.enabled:
            return f"Пост {post_id}: автоподнятие выключено"

        if auto.last_run:
            next_run = auto.last_run + timedelta(days=auto.interval_days)
            if timezone.now() < next_run:
                return f"Пост {post_id}: еще не время (следующее поднятие через {(next_run - timezone.now()).days} дней)"

        old_bounty = auto.post.bounty

        increase = int(old_bounty * auto.percent / 100)
        if increase < 1:
            increase = 1

        auto.post.bounty = old_bounty + increase
        auto.post.save()

        auto.last_run = timezone.now()
        auto.save()

        return f"✅ Пост {post_id} '{auto.post.title}': {old_bounty} → {auto.post.bounty} (+{increase})"

    except PostBountyAuto.DoesNotExist:
        return f"❌ Пост {post_id}: настройки не найдены"


@shared_task
def check_all_posts_bounties():
    """
    Проверяет все посты с включенным автоподнятием и запускает поднятие баунти
    Запускать каждый день в полночь
    """
    from .models import PostBountyAuto

    auto_posts = PostBountyAuto.objects.filter(enabled=True)

    if not auto_posts.exists():
        return "Нет постов с включенным автоподнятием"

    results = []
    for auto in auto_posts:
        result = increase_single_post_bounty.delay(auto.post.id)
        results.append(f"Пост {auto.post.id}: задача запущена (ID: {result.id})")

    return f"Запущено задач: {len(results)}\n" + "\n".join(results)


@shared_task
def test_task():
    """Тестовая задача для проверки работы Celery"""
    return f"Celery работает! Время: {timezone.now()}"