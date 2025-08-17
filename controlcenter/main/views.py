import json
import telebot
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Инициализируем нашего бота
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)

# Здесь мы будем хранить всю логику нашего бота из bot.py
# (пока только обработчик /start для примера)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Вебхук работает! Привет от Django!")

# --- НАШ НОВЫЙ WEBHOOK-ОБРАБОТЧИК ---
@csrf_exempt
def telegram_webhook(request):
    if request.headers.get('content-type') == 'application/json':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse('OK', status=200)
    else:
        return HttpResponseForbidden('Forbidden')