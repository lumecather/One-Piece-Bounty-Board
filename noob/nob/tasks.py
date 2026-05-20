from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import smtplib

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_email, username):
    """
    Отправляет приветственное письмо новому пирату.
    При неудаче повторяет попытку 3 раза с задержкой 60 секунд.
    """
    try:
        send_mail(
            subject='Добро пожаловать на борт! 🏴‍☠️',
            message=f'Привет, {username}! Ты стал пиратом. Лови свою первую награду — 100 белл!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f'Письмо отправлено {user_email}')
        return f'Письмо отправлено {user_email}'
    except smtplib.SMTPException as exc:
        logger.warning(f'Ошибка отправки письма {user_email}: {exc}. Повторная попытка {self.request.retries + 1}')
        raise self.retry(exc=exc)
    except Exception as exc:
        logger.error(f'Неожиданная ошибка при отправке письма {user_email}: {exc}')
        # Для неожиданных ошибок тоже пробуем повторить
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def increase_single_post_bounty(self, post_id):
    """
    Поднимает баунти у конкретного поста по его индивидуальным настройкам.
    """
    from .models import Post, PostBountyAuto

    try:
        auto = PostBountyAuto.objects.get(post_id=post_id)
    except PostBountyAuto.DoesNotExist:
        logger.error(f'Настройки автоподнятия для поста {post_id} не найдены')
        return f"❌ Пост {post_id}: настройки не найдены"

    if not auto.enabled:
        return f"Пост {post_id}: автоподнятие выключено"

    # Проверка времени
    if auto.last_run:
        next_run = auto.last_run + timedelta(days=auto.interval_days)
        if timezone.now() < next_run:
            days_left = (next_run - timezone.now()).days
            return f"Пост {post_id}: ещё не время (следующее поднятие через {days_left} дн.)"

    try:
        old_bounty = auto.post.bounty
        increase = int(old_bounty * auto.percent / 100)
        if increase < 1:
            increase = 1

        auto.post.bounty = old_bounty + increase
        auto.post.save()

        auto.last_run = timezone.now()
        auto.save()

        msg = f"✅ Пост {post_id} '{auto.post.title}': {old_bounty} → {auto.post.bounty} (+{increase})"
        logger.info(msg)
        return msg

    except Exception as exc:
        logger.error(f'Ошибка увеличения баунти поста {post_id}: {exc}')
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def check_all_posts_bounties(self):
    """
    Проверяет все посты с включённым автоподнятием и запускает задачи на поднятие.
    Запускать раз в сутки.
    """
    from .models import PostBountyAuto

    try:
        auto_posts = PostBountyAuto.objects.filter(enabled=True)
        if not auto_posts.exists():
            return "Нет постов с включённым автоподнятием"

        results = []
        for auto in auto_posts:
            # Запускаем отдельную задачу с повторами
            result = increase_single_post_bounty.delay(auto.post.id)
            results.append(f"Пост {auto.post.id}: задача запущена (ID: {result.id})")

        summary = f"Запущено задач: {len(results)}\n" + "\n".join(results)
        logger.info(summary)
        return summary

    except Exception as exc:
        logger.error(f'Ошибка при запуске массовой проверки баунти: {exc}')
        raise self.retry(exc=exc)
