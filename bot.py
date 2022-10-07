import telebot
from db.mysql_db import DB
from steam_totm.guard import Guard
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


db = DB(
    os.environ.get('MYSQL_HOST'),
    os.environ.get('MYSQL_USER'),
    os.environ.get('MYSQL_PASSWORD'),
    os.environ.get('MYSQL_DATABASE')
)

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

user_secret_name = {}
user_step = {}

def get_user_step(user_id):
    if user_id in user_step:
        return user_step[user_id]
    else:
        user_step[user_id] = 0
        return 0

@bot.message_handler(func=lambda message: message.text in ['/start', 'Назад'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row('Все аккаунты', 'Добавить аккаунт')
    markup.row('Удалить аккаунт')
    bot.send_message(message.chat.id, 'Бот', reply_markup=markup)
    
    user_step[message.chat.id] = 0

@bot.message_handler(func=lambda message: message.text in ['/add', 'Добавить аккаунт'])
def add(message):
    bot.send_message(message.chat.id, 'Введите название аккаунта')
    bot.register_next_step_handler(message, get_name)

def get_name(message):
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
    
def get_secret(message):
    secret = message.text
    
    user_id = message.chat.id
    
    res = db.set_secret(user_id, user_secret_name[user_id], secret)
    
    if res.code:
        bot.send_message(user_id, res.message)
        bot.register_next_step_handler(message, get_secret)
    
    bot.send_message(user_id, 'Аккаунт успешно добавлен')

@bot.message_handler(func=lambda message: message.text in ['/list', 'Все аккаунты'])
def list(message):
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
def guard_code(message):
    name = message.text
    secret = db.get_secret(message.chat.id, name)
    guard = Guard(secret)
    code = guard.get_code()
    bot.send_message(message.chat.id, code)

@bot.message_handler(func=lambda message: message.text in ['/delete', 'Удалить аккаунт'])
def delete_list(message):
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
def delete(message):
    name = message.text
    
    res = db.delete_secret(message.chat.id, name)
    if res.code:
        bot.send_message(message.chat.id, res.message)
        bot.register_next_step_handler(message, delete)
        return
    
    bot.send_message(message.chat.id, 'Аккаунт успешно удалён')
    user_step[message.chat.id] = 0

bot.infinity_polling()
