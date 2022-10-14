import telebot
from telebot import types
from db import DB
from steam_totm import Guard
import os
from dotenv import load_dotenv, find_dotenv
from aiohttp import web

load_dotenv(find_dotenv())

BOT_TOKEN = os.environ.get('BOT_TOKEN') or ''

WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT')
WEBHOOK_LISTEN = os.environ.get('WEBHOOK_LISTEN')

# TODO add port from config
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:443"
WEBHOOK_URL_PATH = f"/{BOT_TOKEN}/"

bot = telebot.TeleBot(BOT_TOKEN)

app = web.Application()

async def handle(request):

    request_body_dict = await request.json()
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return web.Response(status=200)

app.router.add_post('/{BOT_TOKEN}/', handle)

db = DB(
    os.environ.get('MYSQL_HOST') or 'localhost',
    os.environ.get('MYSQL_USER') or 'user',
    os.environ.get('MYSQL_PASSWORD') or 'password',
    os.environ.get('MYSQL_DATABASE') or 'steam_guard_bot'
)


user_secret_name = {}
user_step = {}

def get_user_step(user_id):
    if user_id in user_step:
        return user_step[user_id]
    else:
        user_step[user_id] = 0
        return 0

@bot.message_handler(func=lambda message: message.text in ['/start', 'Назад'])
def start(message: types.Message):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row('Все аккаунты', 'Добавить аккаунт')
    markup.row('Удалить аккаунт')
    bot.send_message(message.chat.id, 'Бот', reply_markup=markup)
    
    user_step[message.chat.id] = 0

@bot.message_handler(func=lambda message: message.text in ['/add', 'Добавить аккаунт'])
def add(message: types.Message):
    bot.send_message(message.chat.id, 'Введите название аккаунта')
    bot.register_next_step_handler(message, get_name)

def get_name(message: types.Message, content_types=['text']):
    name = message.text
    
    if name == 'exit':
        start(message)
        return
    
    if db.is_exist(message.chat.id, name):
        bot.send_message(message.chat.id, 'Название уже занято!\nПопробуйте другое или напишите exit что-бы выйти.')
        bot.register_next_step_handler(message, get_name)
        return
    
    user_secret_name[message.chat.id] = name
    bot.send_message(message.chat.id, 'Введите секретный ключ')
    bot.register_next_step_handler(message, get_secret)
    
def get_secret(message: types.Message, content_types=['text']):
    secret = message.text
    
    user_id = message.chat.id
    
    res = db.set_secret(user_id, user_secret_name[user_id], secret)
    
    if res.code:
        bot.send_message(user_id, res.message)
        bot.register_next_step_handler(message, get_secret)
    
    bot.send_message(user_id, 'Аккаунт успешно добавлен')

@bot.message_handler(func=lambda message: message.text in ['/list', 'Все аккаунты'])
def list(message: types.Message):
    names = db.get_user_secrets_name(message.chat.id)
    
    if names == []:
        bot.send_message(message.chat.id, 'У вас нет добавленных аккаунтов')
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for name in names:
        markup.row(name)
    
    markup.row('Назад')
        
    bot.send_message(message.chat.id, 'Лист', reply_markup=markup)
    user_step[message.chat.id] = 2

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 2)
def guard_code(message: types.Message):
    name = message.text
    secret = db.get_secret(message.chat.id, name)
    if secret == None:
        bot.send_message(message.chat.id, 'Код не найден')
        return
    guard = Guard(secret)
    code = guard.get_code()
    bot.send_message(message.chat.id, code)

@bot.message_handler(func=lambda message: message.text in ['/delete', 'Удалить аккаунт'])
def delete_list(message: types.Message):
    names = db.get_user_secrets_name(message.chat.id)
    
    if names is []:
        bot.send_message(message.chat.id, 'У вас нет добавленных аккаунтов')
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for name in names:
        markup.row(name)
    
    markup.row('Назад')
        
    bot.send_message(message.chat.id, 'Лист', reply_markup=markup)
    user_step[message.chat.id] = 1

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def delete(message: types.Message):
    name = message.text
    
    res = db.delete_secret(message.chat.id, name)
    if res.code:
        bot.send_message(message.chat.id, res.message)
        bot.register_next_step_handler(message, delete)
        return
    
    bot.send_message(message.chat.id, 'Аккаунт успешно удалён')
    user_step[message.chat.id] = 0

bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
)
