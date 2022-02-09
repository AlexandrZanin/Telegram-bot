'''main.py основной скрипт который запускает работу,
в нем должны быть нужные импорты и функции которые используют декораторы message_handler и подобные.
'''
import os
import telebot
from telebot import types
from dotenv import load_dotenv
import loader
import orm
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from calendar_my import  MyStyleCalendar
import re
from datetime import date
from loguru import logger
logger.add('loging.log', format="<green>{time:YYYY-MM-DD   HH:mm:ss.SSS}</green> {level} {message}", level="DEBUG")
def env_token():
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
         load_dotenv(dotenv_path)
    token=os.getenv('BOT_TOKEN')
    return token


bot=telebot.TeleBot(env_token())

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ Жми /help")
    logger.info("lets start")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Это бот для поиска отелей.')
    bot.send_message(message.chat.id, '\n'.join(loader.comands_list))

@bot.message_handler(commands=['lowprice'])
def lowprice_message(message):
    loader.registration(message)
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, loader.check_city)
@bot.message_handler(commands=['highprice'])
def highprice_message(message):
    loader.registration(message)
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, loader.check_city)
@bot.message_handler(commands=['bestdeal'])
def bestdeal_message(message):
    loader.registration(message)
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, loader.check_city)

@bot.message_handler(commands=['history'])# история запросов
def history_message(message):
    if orm.Guest.select():
        markup=types.InlineKeyboardMarkup()
        counter=0
        for id_request in orm.Guest.select().where(orm.Guest.user_id == message.from_user.id).order_by(orm.Guest.time_now.desc()):
            if id_request.cmd=='/bestdeal':
                text_button="{time_now}\nКоманда: {cmd}\nГород: {sity}\n{in_date}\n{out_date}\
                \nДиапазон цен: {min_price}-{max_price}\nРасстояние до центра: {max_dist}".\
                    format(time_now=id_request.time_now[:-7], cmd=id_request.cmd, sity=id_request.sity,
                           in_date=id_request.date_in, out_date=id_request.date_out, min_price=id_request.low_price,
                           max_price=id_request.top_price, max_dist=id_request.max_dist)
            else:
                text_button="{time_now}\nКоманда {cmd}\nГород: {sity}\n{in_date}\n{out_date}". \
                    format(time_now=id_request.time_now[:-7], cmd=id_request.cmd, sity=id_request.sity, in_date=id_request.date_in,
                           out_date=id_request.date_out,)
            # markup.add(types.InlineKeyboardButton(text='Подробнее', callback_data='id'+str(id_request.id)))
            loader.get_keyboard(data='id' + str(id_request.id), text=text_button, message=message)
            counter+=1
            if counter==5:
                break
        bot.send_message(message.chat.id, text="Последние {} запросов".format(counter), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="Не выполнено ни одного запроса")

@bot.message_handler(content_types='text')
def some_text(message):
    if message.text=='Да':
        user=loader.user_dict[message.chat.id]
        user.foto=True
        bot.send_message(message.chat.id, 'Сколько фото выводить (не больше 10)?',
                         reply_markup=types.ReplyKeyboardRemove())

        bot.register_next_step_handler(message, get_count_foto)
    elif message.text == 'Нет':
        loader.get_hotels(message)
    else:
        bot.send_message(message.chat.id, 'Не понятно, нажми /help')


@bot.callback_query_handler(func=lambda call: call.data.startswith('yes'))
def callback_worker(query):
    if query.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        user=loader.user_dict[query.message.chat.id]
        user.foto=True
        bot.send_message(query.message.chat.id, 'Сколько фото выводить (не больше 10)?',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, loader.get_hotels)

@bot.callback_query_handler(func=lambda call: call.data.startswith('no'))
def callback_worker(query):
    if query.data=="no":
        loader.get_hotels(query.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('again'))#кнопка ввести другой город
def callback_worker(query):
    if query.data=='again':
        bot.send_message(query.message.chat.id, text='Выберите город для поиска отелей', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, loader.check_city)

@bot.callback_query_handler(func=lambda call: re.search(r'^\d', call.data))#кнопка выбора города из вариантов
def callback_worker(query):
    user=loader.user_dict[query.message.chat.id]
    #print(query.message.reply_markup.keyboard)
    user.sity_id=query.data
    user.sity=user.city_name_id[user.sity_id]
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                          text='Вы выбрали {}'.format(user.sity))
    loader.calendar_func_in(query.message.chat.id)
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
    user=loader.user_dict[c.message.chat.id]
    if not user.date_in:
        result, key, step =  MyStyleCalendar(min_date=date.today(), max_date=date(2023, 12, 31)).process(c.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                       c.message.chat.id,
                                       c.message.message_id,
                                       reply_markup=key)
        elif result:
            bot.edit_message_text(f"Вы выбрали {result}",
                                   c.message.chat.id,
                                   c.message.message_id)
            user.date_in=result
            loader.calendar_func_out(c.message.chat.id)
    else:
        result, key, step=MyStyleCalendar(min_date=user.date_in, max_date=date(2023, 12, 31)).process(c.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]}",
                               c.message.chat.id,
                               c.message.message_id,
                               reply_markup=key)
        elif result:
            bot.edit_message_text(f"Вы выбрали {result}",
                               c.message.chat.id,
                               c.message.message_id)
            user.date_out=result
            if user.cmd == '/bestdeal':
                bot.send_message(c.message.chat.id, 'Укажите диапазон цен за ночь в рублях(priceMin-priceMax)',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(c.message, get_price_range)
            else:
                bot.send_message(c.message.chat.id, 'Сколько отелей выводить? (Не больше 10)',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(c.message, get_hotels_count)


def get_hotels_count(message):
    user=loader.user_dict[message.chat.id]
    if message.text.isdigit(): #проверка, что введено число
        hotel_count=int(message.text)
        if hotel_count<=10:
            user.count_hotels=message.text
            keyboard=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1=types.KeyboardButton("Да")
            btn2=types.KeyboardButton("Нет")
            keyboard.add(btn1, btn2)
            '''
            keyboard=types.InlineKeyboardMarkup()  # наша клавиатура
            key_yes=types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
            keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
            key_no=types.InlineKeyboardButton(text='Нет', callback_data='no')
            keyboard.add(key_no)
            '''
            question='Вывести фото?'
            bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
        elif hotel_count>10:
            bot.reply_to(message, 'Число слишком большое, попробуйте ввести ещё раз')
            bot.register_next_step_handler(message, get_hotels_count)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз' )
        bot.register_next_step_handler(message, get_hotels_count)

def get_max_dist(message):
    user=loader.user_dict[message.chat.id]
    if re.findall('\A\d+\Z', message.text) or re.findall('^\d+[.,]+\d+', message.text): #соответствует ли шаблону число или дробное число
        user.max_dist=message.text
        bot.send_message(message.chat.id, 'Сколько отелей выводить? (Не больше 10)')
        bot.register_next_step_handler(message, get_hotels_count)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз')
        bot.register_next_step_handler(message, get_max_dist)

def get_price_range(message):
    if re.search('^\d+[-]\d+', message.text): # проверяем введен ли диапазон по шаблону XXX-XXX
        user=loader.user_dict[message.chat.id]
        user.low_price=re.findall(r'\d+', message.text)[0]
        user.top_price=re.findall(r'\d+', message.text)[1]
        if user.low_price==user.top_price:# если введены два одинаковых числа
            bot.send_message(message.chat.id, 'Введите диапазон (например: 1000-2000)')
            bot.register_next_step_handler(message, get_price_range)
        else:
            if int(user.low_price) > int(user.top_price):  #сортируем, на случай если мин>макс
                user.low_price, user.top_price=user.top_price, user.low_price
            bot.send_message(message.chat.id, 'Введите максимальное расстояние до центра в км (например 0,5)')
            bot.register_next_step_handler(message, get_max_dist)
    else:
        bot.send_message(message.chat.id, 'Введите диапазон (например: 1000-2000)')
        bot.register_next_step_handler(message, get_price_range)

def get_count_foto(message):
    user=loader.user_dict[message.chat.id]
    if message.text.isdigit():
        hotel_count=int(message.text)
        if hotel_count <= 10:
            user.foto_count=message.text
            loader.get_hotels(message)
        elif hotel_count > 10:
            bot.reply_to(message, 'Число слишком большое, попробуйте ввести ещё раз')
            bot.register_next_step_handler(message, get_count_foto)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз')
        bot.register_next_step_handler(message, get_count_foto)
if __name__ == '__main__':
    bot.infinity_polling()
