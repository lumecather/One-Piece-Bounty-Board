import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noob.settings')

app = Celery('nob')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'increase-bounties-every-sunday': {
        'task': 'nob.tasks.increase_bounties',
        # 'schedule': crontab(hour=9, minute=0, day_of_week='sunday'),  # каждое воскресенье в 9:00
        'schedule': crontab(minute='*/1'),  # для теста: каждую минуту
    },
}
