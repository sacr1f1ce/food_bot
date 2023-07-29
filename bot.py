import numpy as np
import json
import telebot
from telebot import types
from collections import defaultdict

from pizza import *
from utils import *

import warnings
warnings.filterwarnings("ignore")


API_TOKEN = '6094466827:AAFDEgnPoqCJiCTheNJgraAWLdzaJWyxI3Y'
bot = telebot.TeleBot(API_TOKEN)

commands = [
    types.BotCommand('menu', 'Меню'),
    types.BotCommand('cart', 'Корзина')
]

bot.set_my_commands(commands)

cart = {}

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id, 
        text='Добро пожаловть в НАЗВАНИЕ_РЕСТОРАНА')


@bot.message_handler(commands=['menu'])
def menu(message):
    keyboard = types.InlineKeyboardMarkup()

    keys = [
        types.InlineKeyboardButton(text='Пицца', callback_data='pizza')
    ]
    
    keyboard.add(*keys)

    bot.send_message(
        message.chat.id, 
        text='Выберите раздел', 
        reply_markup=keyboard
    )


@bot.message_handler(commands=['cart'])
def order(message):
    name = message.from_user.username

    if name not in cart:
        bot.send_message(
            message.chat.id, 
            text='Корзина пуста'
        )
        return 

    keyboard = types.InlineKeyboardMarkup()
    keys = [
        types.InlineKeyboardButton(text='Оформить заказ', callback_data='buy'),
        types.InlineKeyboardButton(text='Очистить корзину', callback_data='reset')
    ]
    keyboard.add(*keys)

    bot.send_message(
        message.chat.id, 
        text=order_text(cart[name]), 
        reply_markup=keyboard
    )
    

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    name = call.from_user.username
    if call.data == 'reset':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id, 
            text='Корзина очищена'
        )

        del cart[name]
    
    elif call.data == 'pizza':
        keyboard = types.InlineKeyboardMarkup()
        keys = [
            types.InlineKeyboardButton(text='Пицца Дьяволо', callback_data='piz_diablo'),
            types.InlineKeyboardButton(text='Пицца пепперони', callback_data='piz_pepperoni'),
            types.InlineKeyboardButton(text='Пицца с креветками', callback_data='piz_shrimp'),
            types.InlineKeyboardButton(text='Пицца со слабосоленым лососем, каперсами и сыром филадельфия', callback_data='piz_fila'),
            types.InlineKeyboardButton(text='Пицца мясная BBQ', callback_data='piz_bbq')
        ]
        keyboard.add(*keys)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id, 
            text='Выберите пиццу',
            reply_markup=keyboard
        )

    elif call.data[:4] == 'piz_':
        pizza = call.data

        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.id
        )

        keyboard = types.InlineKeyboardMarkup()
        keys = [
            types.InlineKeyboardButton(text='В корзину', callback_data='add_' + call.data),
        ]
        keyboard.add(*keys)

        bot.send_photo(
            chat_id=call.message.chat.id,
            photo=open(pizza_path(pizza), 'rb'),
            caption=pizza_descr(pizza),
            reply_markup = keyboard
        )
    
    elif call.data[:4] == 'add_':
        if name not in cart:
            cart[name] = defaultdict(int)
        cart[name][call.data[4:]] += 1

        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.id
        )

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f'Блюдо {call2name[call.data[4:]]} добавлено в корзину'
        )

    
@bot.message_handler(content_types=['text'])
def process_name(message):
    bot.send_message(
        message.chat.id, 
        text=f'Текст не поддерживается, пользуйтесь кнопками.'
        )
    


bot.polling(none_stop=True)
