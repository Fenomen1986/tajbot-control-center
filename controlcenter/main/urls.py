from django.urls import path
from django.conf import settings
from .views import telegram_webhook

urlpatterns = [
    # Создаем секретный адрес, который знает только Telegram
    path(f'webhook/{settings.TELEGRAM_BOT_TOKEN}/', telegram_webhook, name='telegram_webhook'),
]