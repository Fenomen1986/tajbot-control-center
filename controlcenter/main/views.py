import json
import telebot
from telebot import types
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Bot, Lead # Импортируем наши модели для работы с базой данных

# --- Инициализация ---
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)
# Словарь для временного хранения состояния диалога с пользователями
user_data = {} 

# --- Тексты на двух языках ---
texts = {
    'ru': {
        'welcome': "Здравствуйте!\nДля продолжения, пожалуйста, выберите язык общения.",
        'menu_prompt': "Я ваш цифровой ассистент. Чем могу помочь?",
        'menu_discuss_project': "Обсудить мой проект",
        'ask_name': "Отлично! Как я могу к вам обращаться?",
        'ask_business': "Приятно познакомиться, {}!\nРасскажите коротко о вашем бизнесе (например, 'кафе').",
        'ask_task': "Спасибо! Какую главную задачу вы бы хотели поручить боту?",
        'final_thanks': "Превосходно! Спасибо за ответы. Ваша заявка сохранена. Наш руководитель скоро свяжется с вами.",
    },
    'tj': {
        'welcome': "Ассалому алейкум!\nБарои идома, лутфан забони муоширатро интихоб кунед.",
        'menu_prompt': "Ман ёрдамчии рақамии шумо. Чӣ хизмат карда метавонам?",
        'menu_discuss_project': "Лоиҳаи худро муҳокима кардан",
        'ask_name': "Олӣ! Ба шумо чӣ тавр муроҷиат кунам?",
        'ask_business': "Аз шиносоӣ бо шумо шодам, {}!\nДар бораи тиҷорати худ мухтасар нақл кунед.",
        'ask_task': "Ташаккур! Кадом вазифаи асосиро ба бот супоридан мехоҳед?",
        'final_thanks': "Беҳтарин! Ташаккур барои ҷавобҳо. Дархости шумо сабт шуд. Роҳбари мо ба зудӣ бо шумо дар тамос хоҳад шуд.",
    }
}


# --- ОБРАБОТЧИКИ КОМАНД И СООБЩЕНИЙ (Вся логика бота здесь) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_tj = types.InlineKeyboardButton("Тоҷикӣ", callback_data='lang_tj')
    btn_ru = types.InlineKeyboardButton("Русский", callback_data='lang_ru')
    markup.add(btn_tj, btn_ru)
    welcome_text = f"{texts['tj']['welcome']}\n\n{texts['ru']['welcome']}"
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    user_id = call.message.chat.id
    lang = call.data.split('_')[1]
    user_data[user_id] = {'lang': lang}
    bot.answer_callback_query(call.id)
    bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(texts[lang]['menu_discuss_project'])
    bot.send_message(user_id, texts[lang]['menu_prompt'], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        send_welcome(message)
        return
    lang = user_data[user_id]['lang']
    if message.text == texts[lang]['menu_discuss_project']:
        msg = bot.send_message(user_id, texts[lang]['ask_name'], reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    user_id = message.chat.id
    user_data[user_id]['name'] = message.text
    lang = user_data[user_id]['lang']
    msg = bot.send_message(user_id, texts[lang]['ask_business'].format(message.text))
    bot.register_next_step_handler(msg, process_business_step)

def process_business_step(message):
    user_id = message.chat.id
    user_data[user_id]['business'] = message.text
    lang = user_data[user_id]['lang']
    msg = bot.send_message(user_id, texts[lang]['ask_task'])
    bot.register_next_step_handler(msg, process_task_step)

def process_task_step(message):
    user_id = message.chat.id
    user_data[user_id]['task'] = message.text
    lang = user_data[user_id]['lang']
    
    # --- ИНТЕГРАЦИЯ С БАЗОЙ ДАННЫХ ---
    try:
        # Находим в админке нашего бота по его токену
        bot_instance = Bot.objects.get(token=settings.TELEGRAM_BOT_TOKEN)
        
        name = user_data[user_id].get('name', 'Не указано')
        business = user_data[user_id].get('business', 'Не указано')
        task = user_data[user_id].get('task', 'Не указано')
        
        full_lead_data = (
            f"Бизнес: {business}\n"
            f"Задача: {task}\n"
            f"Язык: {'Русский' if lang == 'ru' else 'Тоҷикӣ'}"
        )
        
        # Создаем новую Заявку (Лид) в нашей базе данных
        Lead.objects.create(
            bot=bot_instance,
            customer_name=name,
            customer_data=full_lead_data,
            status='Новая'
        )
        bot.send_message(user_id, texts[lang]['final_thanks'])
        print(f"New lead from {name} saved to DB.")

    except Bot.DoesNotExist:
        print(f"CRITICAL ERROR: A bot with the token from settings.py is not registered in the admin panel!")
        bot.send_message(user_id, "Произошла системная ошибка. Пожалуйста, попробуйте позже.")
    except Exception as e:
        print(f"CRITICAL ERROR during lead saving: {e}")
        bot.send_message(user_id, "Произошла системная ошибка. Пожалуйста, попробуйте позже.")
    
    del user_data[user_id]


# --- WEBHOOK-ОБРАБОТЧИК (Остается без изменений) ---
@csrf_exempt
def telegram_webhook(request):
    if request.headers.get('content-type') == 'application/json':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse('OK', status=200)
    else:
        return HttpResponseForbidden('Forbidden')