import logging
import os

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta
from django.utils import timezone
from django.utils.html import strip_tags
from django.template.loader import render_to_string


from news.models import Post, Category


from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_fresh_news_list_to_subs():
    categories = Category.objects.all()
    week_ago = timezone.now() - timedelta(days=7)
    fresh_news = Post.objects.filter(creation_time__gt=week_ago)

    for category in categories:
        fresh_news_in_category = fresh_news.filter(categories=category)
        recipients = []
        for subscriber in category.subscribers.all():
            recipients.append(subscriber.email)
        html_content = render_to_string('mail_news_list.html', {'news_list': fresh_news_in_category})
        msg = EmailMultiAlternatives(
            subject="Свежие новости за неделю",
            body=strip_tags(html_content),
            from_email=os.getenv("YANDEX_ADDRESS"),
            to=recipients,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=700_000):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_fresh_news_list_to_subs,
            trigger=CronTrigger(
                day_of_week="sun", hour="00", minute="00"
            ),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),

            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
