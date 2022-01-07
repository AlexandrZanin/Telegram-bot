'''main.py основной скрипт который запускает работу,
в нем должны быть нужные импорты и функции которые используют декораторы message_handler и подобные.
'''
import os
import telebot
from dotenv import load_dotenv
from loader import *
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from calendar_my import  MyStyleCalendar
def env_token():
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
         load_dotenv(dotenv_path)

    # bot_token="2135158305: AAEV80YY - mTzlXAVqYS5FgGjuwe0Ef9l2yU"
    token=os.getenv('BOT_TOKEN')
    return token


bot=telebot.TeleBot(env_token())

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ Жми /help")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Это бот для поиска отелей.')
    bot.send_message(message.chat.id, '\n'.join(comands_list))

@bot.message_handler(commands=['lowprice'])
def lowprice_message(message):
    registration(message)
    # user=User(message.text)
    # user_dict[message.from_user.id]=user
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_sity)
@bot.message_handler(commands=['highprice'])
def highprice_message(message):
    registration(message)
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_sity)
@bot.message_handler(commands=['bestdeal'])
def bestdeal_message(message):
    registration(message)
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_sity)

@bot.message_handler(commands=['history'])# история запросов
def history_message(message):
    if orm.Guest.select():
        markup=types.InlineKeyboardMarkup()
        counter=0
        for id_request in orm.Guest.select().order_by(orm.Guest.time_now.desc()):
            text_button="{time_now}\n{sity}\n{in_date}\n{out_date}". \
                format(time_now=id_request.time_now[:-7], cmd=id_request.cmd, sity=id_request.sity, in_date=id_request.date_in,
                       out_date=id_request.date_out,)
            # markup.add(types.InlineKeyboardButton(text='Подробнее', callback_data='id'+str(id_request.id)))
            get_keyboard(data='id' + str(id_request.id), text=text_button, message=message)
            counter+=1
            if counter==5:
                break
        bot.send_message(message.chat.id, text="Последние {} запросов".format(counter), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="Не выполнено ни одного запроса")

@bot.message_handler(content_types='text')
def some_text(message):
    bot.send_message(message.chat.id, 'Не понятно, нажми /help')


@bot.callback_query_handler(func=lambda call: call.data.startswith('yes'))
def callback_worker(query):
    if query.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        user=user_dict[query.message.chat.id]
        user.foto=True
        bot.send_message(query.message.chat.id, 'Сколько фото выводить?',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, get_hotels)

@bot.callback_query_handler(func=lambda call: call.data.startswith('no'))
def callback_worker(query):
    if query.data=="no":
        get_hotels(query.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('again'))
def callback_worker(query):
    if query.data=='again':
        bot.send_message(query.message.chat.id, text='Выберите город для поиска отелей', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, check_sity)

@bot.callback_query_handler(func=lambda call: re.search(r'^\d+', call.data))
def callback_worker(query):
    user=user_dict[query.message.chat.id]
    user.sity_id=query.data
    calendar_func_in(query.message.chat.id)
        # bot.register_next_step_handler(query.message, get_date_in)

@bot.callback_query_handler(func=lambda call: re.search(r'[id]\d+', call.data))
def callback_worker(query):
    query.data=int(query.data[2:])
    for hotel in orm.Hotels_find.select().where(orm.Hotels_find.owner_id==query.data):
        text="{name}\n{dist}\n{addres}\n{price}\n{stars}\n{site}".\
            format(name=hotel.name, dist=hotel.dist,
                               addres=hotel.addres, price=hotel.price,
                               stars=hotel.stars,site=hotel.site)
        bot.send_message(query.message.chat.id, text,
                         reply_markup=types.ReplyKeyboardRemove())
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step =  MyStyleCalendar().process(c.data)

    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)
        user = user_dict[c.message.chat.id]
        if user.date_in==None:
            user.date_in = result
            calendar_func_out(c.message.chat.id)
        else:
            user.date_out = result
            if user.cmd == '/bestdeal':
                bot.send_message(c.message.chat.id, 'Укажите диапазон цен',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(c.message, get_price_range)
            else:
                bot.send_message(c.message.chat.id, 'Сколько отелей выводить? (Не больше 10)',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(c.message, get_hotels_count)


if __name__ == '__main__':
    bot.infinity_polling()
