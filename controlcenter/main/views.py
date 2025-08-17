import json
import telebot
from telebot import types
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Bot, Lead

# --- Инициализация ---
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)
user_data = {}

# --- Тексты на двух языках (Полная версия) ---
texts = {
    'ru': {
        'welcome': "Здравствуйте!\nДля продолжения, пожалуйста, выберите язык общения.",
        'menu_prompt': "Я ваш цифровой ассистент. Чем могу помочь?",
        'menu_what_bots_can_do': "Узнать, что умеют чат-боты",
        'menu_see_example': "Посмотреть пример работы",
        'menu_discuss_project': "Обсудить мой проект",
        'menu_prices': "Узнать примерные цены",
        'reply_what_bots_can_do': (
            "Наши чат-боты — это полноценные виртуальные сотрудники, которые умеют:\n\n"
            "✅ *Принимать заказы:* для ресторанов, кафе и магазинов.\n"
            "✅ *Записывать на услуги:* для салонов красоты, клиник, автосервисов.\n"
            "✅ *Консультировать:* отвечать на 90% частых вопросов о ценах, адресе, услугах.\n"
            "✅ *Собирать заявки:* и моментально сохранять их в CRM-системе."
        ),
        'reply_see_example': (
            "Отличный выбор! Вместо тысячи слов — один наглядный пример.\n\n"
            "Представьте бота для ресторана:\n"
            "1️⃣ Клиент видит кнопки: 'Меню', 'Заказ', 'Бронь'.\n"
            "2️⃣ Нажимает 'Меню', видит категории: 'Салаты', 'Горячее'.\n"
            "3️⃣ Выбирает блюдо, добавляет в корзину.\n"
            "4️⃣ Нажимает 'Оформить заказ', пишет адрес и телефон.\n\n"
            "Всё! Заказ моментально появляется в вашей админ-панели. Просто, быстро и 24/7."
        ),
        'reply_prices': (
            "Стоимость зависит от сложности задач. Вот наши базовые пакеты:\n\n"
            "🔹 *'Старт' (450 - 2000 сомони):* Бот-визитка с информацией о компании и ответами на частые вопросы (FAQ).\n\n"
            "🔹 *'Бизнес' (2000 - 4000 сомони):* Бот с функцией онлайн-записи или приема простых заказов.\n\n"
            "🔹 *'Профи' (от 4000 сомони):* Сложный бот с интеграцией с вашей CRM-системой или базой данных."
        ),
        'ask_name': "Отлично! Как я могу к вам обращаться?",
        'ask_business': "Приятно познакомиться, {}!\nРасскажите коротко о вашем бизнесе (например, 'кафе', 'магазин').",
        'ask_task': "Спасибо! Какую главную задачу вы бы хотели поручить боту?",
        'final_thanks': "Превосходно! Спасибо за ответы. Ваша заявка сохранена. Наш руководитель скоро свяжется с вами.",
        'error_message': "Произошла системная ошибка. Пожалуйста, попробуйте позже."
    },
    'tj': {
        'welcome': "Ассалому алейкум!\nБарои идома, лутфан забони муоширатро интихоб кунед.",
        'menu_prompt': "Ман ёрдамчии рақамии шумо. Чӣ хизмат карда метавонам?",
        'menu_what_bots_can_do': "Чат-ботҳо чӣ кор карда метавонанд",
        'menu_see_example': "Намунаи корро дидан",
        'menu_discuss_project': "Лоиҳаи худро муҳокима кардан",
        'menu_prices': "Нархҳои тахминиро фаҳмидан",
        'reply_what_bots_can_do': "...",
        'reply_see_example': "...",
        'reply_prices': "...",
        'ask_name': "Олӣ! Ба шумо чӣ тавр муроҷиат кунам?",
        'ask_business': "Аз шиносоӣ бо шумо шодам, {}!\nДар бораи тиҷорати худ мухтасар нақл кунед.",
        'ask_task': "Ташаккур! Кадом вазифаи асосиро ба бот супоридан мехоҳед?",
        'final_thanks': "Беҳтарин! Ташаккур барои ҷавобҳо. Дархости шумо сабт шуд. Роҳбари мо ба зудӣ бо шумо дар тамос хоҳад шуд.",
        'error_message': "Хатогии системавӣ рух дод. Лутфан, дертар кӯшиш кунед."
    }
}

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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(texts[lang]['menu_what_bots_can_do']),
        types.KeyboardButton(texts[lang]['menu_see_example']),
        types.KeyboardButton(texts[lang]['menu_prices']),
        types.KeyboardButton(texts[lang]['menu_discuss_project'])
    )
    bot.send_message(user_id, texts[lang]['menu_prompt'], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        send_welcome(message)
        return
    lang = user_data[user_id]['lang']
    if text == texts[lang]['menu_what_bots_can_do']:
        bot.send_message(user_id, texts[lang]['reply_what_bots_can_do'], parse_mode="Markdown")
    elif text == texts[lang]['menu_see_example']:
        bot.send_message(user_id, texts[lang]['reply_see_example'], parse_mode="Markdown")
    elif text == texts[lang]['menu_prices']:
        bot.send_message(user_id, texts[lang]['reply_prices'], parse_mode="Markdown")
    elif text == texts[lang]['menu_discuss_project']:
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
    
    # --- УЛУЧШЕННЫЙ БЛОК ИНТЕГРАЦИИ С БД ---
    try:
        token_from_settings = settings.TELEGRAM_BOT_TOKEN
        if not token_from_settings:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")
        
        bot_instance = Bot.objects.get(token=token_from_settings)
        
        name = user_data[user_id].get('name', 'Не указано')
        business = user_data[user_id].get('business', 'Не указано')
        task = user_data[user_id].get('task', 'Не указано')
        
        full_lead_data = (f"Бизнес: {business}\nЗадача: {task}\nЯзык: {'Русский' if lang == 'ru' else 'Тоҷикӣ'}")
        
        Lead.objects.create(
            bot=bot_instance,
            customer_name=name,
            customer_data=full_lead_data,
            status='Новая'
        )
        bot.send_message(user_id, texts[lang]['final_thanks'])
        print(f"✅ New lead from '{name}' saved to DB.")

    except Bot.DoesNotExist:
        error_message = f"🛑 CRITICAL ERROR: A bot with the token '{settings.TELEGRAM_BOT_TOKEN[:15]}...' is NOT registered in the admin panel!"
        print(error_message)
        bot.send_message(user_id, texts[lang]['error_message'])
    except Exception as e:
        error_message = f"🛑 CRITICAL ERROR during lead saving: {e}"
        print(error_message)
        bot.send_message(user_id, texts[lang]['error_message'])
    
    del user_data[user_id]


@csrf_exempt
def telegram_webhook(request):
    if request.headers.get('content-type') == 'application/json':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse('OK', status=200)
    else:
        return HttpResponseForbidden('Forbidden')