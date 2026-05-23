import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noob.settings')

app = Celery('nob')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-all-posts-bounties': {
        'task': 'nob.tasks.check_all_posts_bounties',
        'schedule': crontab(hour=0, minute=0),
        # 'schedule': crontab(minute='*/1'),  # for test
    },

    # Тестовая задача для проверки (раскомментировать для теста)
    # 'test-task': {
    #     'task': 'nob.tasks.test_task',
    #     'schedule': crontab(minute='*/5')
    # },
}