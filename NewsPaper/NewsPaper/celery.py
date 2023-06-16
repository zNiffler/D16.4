import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_fresh_news_every_week': {
        'task': 'news.tasks.send_fresh_news_list_to_subs',
        'schedule': crontab(day_of_week='monday', hour=8)
    }
}
