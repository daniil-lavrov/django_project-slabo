import gevent
import pytz as pytz
from celery import shared_task
import telebot
from .models import User
from django.utils import timezone

@shared_task
def send_statistic():
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = timezone.now().astimezone(moscow_tz)
    start_of_today = moscow_tz.localize(timezone.datetime(now.year, now.month, now.day, 0, 0, 0))
    end_of_today = moscow_tz.localize(timezone.datetime(now.year, now.month, now.day, 23, 59, 59))
    today_users = User.objects.filter(created_at__range=(start_of_today, end_of_today))

    bot = telebot.TeleBot("7014662631:AAHinU7mhDTPnT0dWN5zXtFtpLj0C-Jlqb8")

    if today_users.exists():
        num_of_today_reg = len(list(today_users))
        bot.send_message(chat_id=780024041, text=f'Сегодня зарегестрировалось {num_of_today_reg} пользователей')
    else:
        print("Пользователи не зарегистрированы сегодня.")


