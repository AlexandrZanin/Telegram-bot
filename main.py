'''main.py основной скрипт который запускает работу,
в нем должны быть нужные импорты и функции которые используют декораторы message_handler и подобные.
'''

from telebot import types
from loader import bot, registration
import handlers
import orm
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from calendar_my import  MyStyleCalendar
import re
from datetime import date, timedelta
from loguru import logger
from userclass import User
logger.add('loging.log', format="<green>{time:YYYY-MM-DD   HH:mm:ss.SSS}</green> {level} {message}", level="DEBUG")

comands_list=['/lowprice - топ самых дешёвых отелей',
              '/highprice - топ самых дорогих отелей',
              '/bestdeal - топ отелей по цене и удалённости от центра',
              '/history - история запросов',
              '/stop - остановить поиск']

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ Жми /help")
    logger.info("lets start")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Это бот для поиска отелей.')
    bot.send_message(message.chat.id, '\n'.join(comands_list))

@bot.message_handler(commands=['lowprice'])
def lowprice_message(message):
    registration(message)
    bot.register_next_step_handler(message, handlers.check_city)
@bot.message_handler(commands=['highprice'])
def highprice_message(message):
    registration(message)
    bot.register_next_step_handler(message, handlers.check_city)
@bot.message_handler(commands=['bestdeal'])
def bestdeal_message(message):
    registration(message)
    bot.register_next_step_handler(message, handlers.check_city)

@bot.message_handler(commands=['history'])# история запросов
def history_message(message:types.Message):
    if orm.Guest.select():
        # markup=types.InlineKeyboardMarkup()
        counter=0
        for id_request in orm.Guest.select().where(orm.Guest.user_id == message.from_user.id).order_by(orm.Guest.time_now.desc()):
            # из базы берутся запросы, которые соответствуют по user.id, отсортированные по времени в порядке убывания
            if id_request.cmd=='/bestdeal':
                text_button="Время запроса: {time_now}\nКоманда: {cmd}\nГород: {sity}\nДата заезда: {in_date}\nДата выезда: {out_date}\
                \nДиапазон цен: {min_price}-{max_price}\nРасстояние до центра: {max_dist}".\
                    format(time_now=id_request.time_now[:-7], cmd=id_request.cmd, sity=id_request.sity,
                           in_date=id_request.date_in, out_date=id_request.date_out, min_price=id_request.low_price,
                           max_price=id_request.top_price, max_dist=id_request.max_dist)
            else:
                text_button="Время запроса: {time_now}\nКоманда {cmd}\nГород: {sity}\nДата заезда: {in_date}\nДата выезда: {out_date}". \
                    format(time_now=id_request.time_now[:-7], cmd=id_request.cmd, sity=id_request.sity, in_date=id_request.date_in,
                           out_date=id_request.date_out,)
            # markup.add(types.InlineKeyboardButton(text='Подробнее', callback_data='id'+str(id_request.id)))
            handlers.get_keyboard(data='id' + str(id_request.id), text=text_button, message=message)
            counter+=1
            if counter==5:
                break
        if counter==1:ending=""
        elif counter==5:ending="ов"
        else:ending="а"

        bot.send_message(message.chat.id, text="Последние {} запрос{}".format(counter, ending), reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, text="Не выполнено ни одного запроса")

@bot.message_handler(commands=['stop'])
def stop_message(message):
    bot.send_message(message.chat.id, 'Выполните новый поиск',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, '\n'.join(comands_list))
    logger.info("User {} press stop".format(message.from_user.id))


@bot.message_handler(content_types='text')
def some_text(message:types.Message):
    if message.text=='Да':
        user=User.get_user(message.chat.id)
        user.foto=True
        bot.send_message(message.chat.id, 'Сколько фото выводить (не больше 10)?',
                         reply_markup=types.ReplyKeyboardRemove())

        bot.register_next_step_handler(message, get_count_foto)
    elif message.text == 'Нет':
        handlers.get_hotels(message)
    else:
        bot.send_message(message.chat.id, 'Не понятно, нажми /help')


@bot.callback_query_handler(func=lambda call: call.data.startswith('yes'))
def callback_worker(query):
    if query.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        user=User.get_user(query.message.chat.id)
        user.foto=True
        bot.send_message(query.message.chat.id, 'Сколько фото выводить (не больше 10)?',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, handlers.get_hotels)

@bot.callback_query_handler(func=lambda call: call.data.startswith('no'))
def callback_worker(query):
    if query.data=="no":
        handlers.get_hotels(query.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('again'))#кнопка ввести другой город
def callback_worker(query):
    if query.data=='again':
        bot.send_message(query.message.chat.id, text='Выберите город для поиска отелей', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, handlers.check_city)

@bot.callback_query_handler(func=lambda call: re.search(r'^\d', call.data))#кнопка выбора города из вариантов
def callback_worker(query):
    user=User.get_user(query.message.chat.id)
    user.sity_id=query.data
    user.sity=user.city_name_id[user.sity_id]
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                          text='Вы выбрали {}'.format(user.sity))
    handlers.calendar_func_in(query.message.chat.id)
        # bot.register_next_step_handler(query.message, get_date_in)

@bot.callback_query_handler(func=lambda call: re.search(r'[id]\d+', call.data))#кнопка "смотреть подробнее" в history
def callback_worker(query):
    query.data=int(query.data[2:])
    for hotel in orm.Hotels_find.select().where(orm.Hotels_find.owner_id==query.data):
        handlers.send_info(hotel, query.message.chat.id)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    user=User.get_user(c.message.chat.id)
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
            handlers.calendar_func_out(c.message.chat.id)
    else:
        result, key, step=MyStyleCalendar(min_date=user.date_in+timedelta(days=+1), max_date=date(2023, 12, 31)).process(c.data)
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


def get_hotels_count(message:types.Message):
    user=User.get_user(message.chat.id)
    if message.text=='/stop':
        bot.register_next_step_handler(message, stop_message)
    if message.text.isdigit(): #проверка, что введено число
        hotel_count=int(message.text)
        if hotel_count<=10:
            user.count_hotels=message.text
            keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.row('Да', 'Нет')
            question='Вывести фото?'
            bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
        elif hotel_count>10:
            bot.reply_to(message, 'Число слишком большое, попробуйте ввести ещё раз')
            bot.register_next_step_handler(message, get_hotels_count)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз' )
        bot.register_next_step_handler(message, get_hotels_count)

def get_max_dist(message:types.Message):
    user=User.get_user(message.chat.id)

    if re.findall('\A\d+\Z', message.text) or re.findall('^\d+[.,]+\d+', message.text): #соответствует ли шаблону число или дробное число
        user.max_dist=message.text
        bot.send_message(message.chat.id, 'Сколько отелей выводить? (Не больше 10)')
        bot.register_next_step_handler(message, get_hotels_count)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз')
        bot.register_next_step_handler(message, get_max_dist)

def get_price_range(message:types.Message):
    if re.search('^\d+[-]\d+', message.text): # проверяем введен ли диапазон по шаблону XXX-XXX
        user=User.get_user(message.chat.id)
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
        bot.edit_message_text(message.chat.id, 'Введите диапазон (например: 1000-2000)')
        bot.register_next_step_handler(message, get_price_range)

def get_count_foto(message:types.Message):
    user=User.get_user(message.chat.id)
    if message.text.isdigit():
        hotel_count=int(message.text)
        if hotel_count <= 10:
            user.foto_count=message.text
            handlers.get_hotels(message)
        elif hotel_count > 10:
            bot.reply_to(message, 'Число слишком большое, попробуйте ввести ещё раз')
            bot.register_next_step_handler(message, get_count_foto)
    else:
        bot.reply_to(message, 'Это не число, попробуйте ввести ещё раз')
        bot.register_next_step_handler(message, get_count_foto)
if __name__ == '__main__':
    bot.infinity_polling()
