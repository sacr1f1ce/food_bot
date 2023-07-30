from pizza import *

def order_text(cart):
    total = 0
    msg = ''
    for i, (item, count) in enumerate(cart.items()):
        msg += f'{i + 1}. {call2name[item]} | {count} x {price[item]} руб. \n'
        total += count * price[item]
    msg += f'\n Итого {total} рублей'
    return msg

def order_details(cart, mobile, adress, payment):
    msg = order_text(cart)
    msg += f'\n Номер телефона: {mobile} \n'
    msg += f'\n Адрес: {adress} \n'
    msg += f'\n Способ оплаты: {payment}'
    return msg
