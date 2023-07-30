import numpy as np
import json
import telebot
from telebot import types
from collections import defaultdict

from pizza import *
from utils import *

import warnings
warnings.filterwarnings("ignore")

order_id = '-918073133'
API_TOKEN = '6094466827:AAFDEgnPoqCJiCTheNJgraAWLdzaJWyxI3Y'
bot = telebot.TeleBot(API_TOKEN)

commands = [
    types.BotCommand('menu', 'Меню'),
    types.BotCommand('cart', 'Корзина')
]

bot.set_my_commands(commands)

cart = {}
mobile = {}
adress = {}
payment = {}

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id, 
        text='Добро пожаловть в НАЗВАНИЕ_РЕСТОРАНА')
    

@bot.message_handler(func=lambda msg: msg.text is not None and msg.text[0] != '/')
def text_msg(message):
    print(message.chat.id)
    bot.send_message(
        message.chat.id, 
        text=f'Текст не поддерживается, пользуйтесь кнопками.'
        )


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

    elif call.data == 'buy':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id, 
            text='Введите ваш адрес'
        )
        bot.register_next_step_handler(msg, dest)

    elif call.data[:4] == 'pay_':
        if call.data[4:] == 'cash':
            payment[name] = 'Наличные'
        else:
            payment[name] = 'Картой'
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id, 
            text='Спасибо, Ваш заказ принят в обработку'
        )
        
        bot.send_message(
            chat_id=order_id,
            text=order_details(cart[name], mobile[name], adress[name], payment[name])
        )
        

def dest(message):
    name = message.from_user.username
    adress[name] = message.text

    msg = bot.send_message(
            chat_id=message.chat.id,
            #message_id=message.id, 
            text='Введите ваш телефон'
        )
    bot.register_next_step_handler(msg, tele)


def tele(message):
    name = message.from_user.username
    mobile[name] = message.text

    keyboard = types.InlineKeyboardMarkup()
    keys = [
        types.InlineKeyboardButton(text='Наличные', callback_data='pay_cash'),
        types.InlineKeyboardButton(text='Картой', callback_data='pay_card')
    ]
    keyboard.add(*keys)

    bot.send_message(
        chat_id=message.chat.id,
        #message_id=message.id, 
        text='Выберите способ оплаты',
        reply_markup=keyboard
    )

    
bot.polling(none_stop=True)
