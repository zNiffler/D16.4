import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import timedelta
from celery import shared_task
from .models import Post, Category


from dotenv import load_dotenv

load_dotenv()


@shared_task
def mail_new_post_to_subs(post_pk):
    post = Post.objects.get(pk=post_pk)
    categories = post.categories.all()
    html_content = render_to_string('mail_news_single.html', {'header': post.header,
                                                              'text': post.text,
                                                              'id': post.id})
    to = []
    for category in categories:
        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            to.append(subscriber.email)
    msg = EmailMultiAlternatives(
        subject=post.header,
        body=post.text[0:50],
        from_email=os.getenv("YANDEX_ADDRESS"),
        to=to,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
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
