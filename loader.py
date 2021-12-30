'''основной модуль loader.py который погружает все нужное, создает экземпляры если нужны.
В нем должны подгружаться все нужные константы(токены бота, API) инициализироваться класс с ботом TeleBot
'''
import json

import orm
from orm import *
from main import bot
from telebot import types
import apidler
import re
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

user_dict={}
comands_list=['/lowprice - топ самых дешёвых отелей',
              '/highprice - топ самых дорогих отелей',
              '/bestdeal - топ отелей по цене и удалённости от центра',
              '/history - история запросов']


class User:
    def __init__(self, cmd, id):
        self.cmd=cmd
        self.id=id
        self.sity=None
        self.sity_id=None
        self.date_in=None
        self.date_out=None
        self.low_price=0
        self.top_price=0
        self.count_hotels=None
        self.foto=False
        self.foto_count=0
        self.locale='en_US'

# def registration(message):
#   user.get_user_params(message.from_user.id)['sort_order']=
#   user.get_user_params(message.from_user.id)['command']=
#   user.get_user_params(message.from_user.id)['datatime']= datatime.datatime.now()
#   logger.info('Recieved lowprice command from user {}'.formar(message.from_user.id)
def registration(message):
    user=User(message.text, message.from_user.id)
    user_dict[message.from_user.id]=user

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
    get_sity(message)
@bot.message_handler(commands=['highprice'])
def highprice_message(message):
    registration(message)
    # user=User(message.text, message.from_user.id)
    # user_dict[message.from_user.id]=user
    get_sity(message)
@bot.message_handler(commands=['bestdeal'])
def bestdeal_message(message):
    registration(message)
    # user=User(message.text)
    # user_dict[message.from_user.id]=user
    get_sity(message)
@bot.message_handler(commands=['history'])# история запросов
def history_message(message):
    if orm.Guest.select():
        markup=types.InlineKeyboardMarkup()
        counter=0
        for id_request in orm.Guest.select().order_by(orm.Guest.time_now.desc()):
            text_button="️{sity}✌️{in_date}:{out_date}✌️{low}-{top}". \
                format(cmd=id_request.cmd, sity=id_request.sity, in_date=id_request.date_in, out_date=id_request.date_out,
                       low=id_request.low_price, top=id_request.top_price)
            markup.add(types.InlineKeyboardButton(text=text_button, callback_data='id'+str(id_request.id)))
            counter+=1
            if counter==5:
                break
        bot.send_message(message.chat.id, text="Последние {} запросов".format(counter), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="Не выполнено ни одного запроса")

@bot.message_handler(content_types='text')
def some_text(message):
    bot.send_message(message.chat.id, 'Не понятно, нажми /help')
def get_sity(message):
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_sity)

    # bot.send_message(message.chat.id, 'Введите дату заезда в формате ГГГГ-ДД-ММ',
    #                  reply_markup=types.ReplyKeyboardRemove())
    # bot.register_next_step_handler(message, get_date_in)
def check_sity(message):
    user=user_dict[message.chat.id]
    user.sity=message.text
    user.locale=apidler.check_locale(user.sity)
    keyboard=types.InlineKeyboardMarkup()  # наша клавиатура
    try:
        list_sity = apidler.get_sity_destinationID(user.sity, user.locale)
        question='Ничего не найдено'
        for elem in list_sity:
            if elem["type"] == "CITY" and elem['name'].lower() == message.text.lower():
                question='Уточните'
                if re.findall(r'>.*<', elem["caption"]):
                    text_button=re.sub(r'<.*>.*</.*>', elem['name'], elem["caption"])
                else:
                    text_button=elem["caption"]
                key=types.InlineKeyboardButton(text=text_button, callback_data=elem["destinationId"])  # кнопка с инфо об отеле
                keyboard.add(key)  # добавляем кнопку в клавиатуру
        key1=types.InlineKeyboardButton(text='Ввести другой город', callback_data='again')  # кнопка с инфо об отеле
        keyboard.add(key1)  # добавляем кнопку в клавиатуру
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    except ConnectionError as e:
#       logger.error('Api coonection error {}'.format(e))
        bot.send_message(message.from_user.id, 'Ошибка в соединение')
    except TimeoutError as e:
        # logger.error('Api coonection error {}'.format(e))
        bot.send_message(message.from_user.id, 'время истекло')
    except json.decoder.JSONDecodeError as e:
        # logger.error('Api coonection error {}'.format(e))
        bot.send_message(message.from_user.id, 'Некорректный ответ')
'''
@bot.callback_query_handler(func=lambda call: True)
def callback_sity(call):
        # call.data это callback_data, которую мы указали при объявлении кнопки
        # if call.data:
        user=user_dict[call.message.chat.id]
        user.sity_id=call.data
        bot.send_message(call.message.chat.id, 'Введите дату заезда в формате ГГГГ-ДД-ММ',
                              reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(call.message, get_date_in)
'''
def get_date_in(message):
    user=user_dict[message.chat.id]
    user.date_in=message.text
    bot.send_message(message.chat.id, 'Введите дату выезда в формате ГГГГ-ДД-ММ',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_date_out)


def get_date_out(message):
    user=user_dict[message.chat.id]
    user.date_out=message.text
    if user.cmd=='/bestdeal':
        bot.send_message(message.chat.id, 'Укажите диапазон цен',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_price_range)
    else:
        bot.send_message(message.chat.id, 'Сколько отелей выводить?',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_hotels_count)


def get_price_range(message):
    user=user_dict[message.chat.id]
    user.low_price=re.findall(r'\d+', message.text)[0]
    user.top_price=re.findall(r'\d+', message.text)[1]
    bot.send_message(message.chat.id, 'Сколько отелей выводить?',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_hotels_count)


def get_hotels_count(message):
    user=user_dict[message.chat.id]
    user.count_hotels=message.text
    keyboard=types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes=types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no=types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question='Вывести фото?'
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)# отсюда улетает опять на дату
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(query):
    if query.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        user=user_dict[query.message.chat.id]
        user.foto=True
        bot.send_message(query.message.chat.id, 'Сколько фото выводить?',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, get_hotels)
    elif query.data=="no":
        get_hotels(query.message)
    elif query.data=='again':
        bot.send_message(query.message.chat.id, text='Выберите город для поиска отелей', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query.message, check_sity)
    elif re.search(r'^\d+', query.data):
        user=user_dict[query.message.chat.id]
        user.sity_id=query.data
        bot.send_message(query.message.chat.id, 'Введите дату заезда в формате ГГГГ-ДД-ММ',
                         reply_markup=types.ReplyKeyboardRemove())
        calendar_func(query.message.chat.id)
        # bot.register_next_step_handler(query.message, get_date_in)
    elif re.search(r'[id]\d+', query.data):
        query.data=int(query.data[2:])
        for hotel in orm.Hotels_find.select().where(orm.Hotels_find.owner_id==query.data):
            text="{name}\n{dist}\n{addres}\n{price}\n{stars}\n{site}".\
                format(name=hotel.name, dist=hotel.dist,
                                   addres=hotel.addres, price=hotel.price,
                                   stars=hotel.stars,site=hotel.site)
            bot.send_message(query.message.chat.id, text,
                             reply_markup=types.ReplyKeyboardRemove())

def get_hotels(message):
    user=user_dict[message.chat.id]
    user.foto_count=message.text
    bot.send_message(message.chat.id, 'Придется немного подождать')
    orm.create_table_guest()
    new_find=orm.Guest.create(cmd=user.cmd, sity=user.sity, sity_id=user.sity_id,
                          date_in=user.date_in, date_out=user.date_out,
                          low_price=user.low_price, top_price=user.top_price,
                          count_hotels=user.count_hotels, foto=user.foto,
                          foto_count=user.foto_count, user_id = user.id,
                          time_now=datetime.datetime.now())

    if user.cmd=='/lowprice':
        list_hotels=apidler.lowprice_func(user.sity_id, user.count_hotels, user.date_in, user.date_out, user.locale)
    elif user.cmd=='/highprice':
        list_hotels=apidler.highprice_func(user.sity_id, user.count_hotels, user.date_in, user.date_out, user.locale)
    elif user.cmd=='/bestdeal':
        list_hotels=apidler.bestdeal_func(user.sity_id, user.count_hotels, user.date_in, user.date_out,
                                          user.low_price, user.top_price, user.locale)

    for hotel in list_hotels:
        hotel_info={}
        hotel_info['name']=hotel["name"]
        hotel_info['dist']=hotel["landmarks"][0]["distance"]
        details_info = apidler.get_details(hotel['id'], user.date_in, user.date_out, user.locale)
        try:
            hotel_info['addres']=details_info["propertyDescription"]["localisedAddress"]["fullAddress"] # может отсутствовать информация
        except KeyError:
            hotel_info.append('Адрес отсутствует')
        hotel_info['price']=hotel["ratePlan"]["price"]["current"]
        hotel_info['stars']=str(details_info["propertyDescription"]["starRating"])
        hotel_info['site']='https://ru.hotels.com/ho'+str(hotel['id'])
        bot.send_message(message.chat.id, '\n'.join(hotel_info.values()))
        orm.create_table_hotels()
        orm.Hotels_find.create(owner=new_find, name=hotel_info['name'], dist=hotel_info['dist'],
                               addres=hotel_info['addres'], price=hotel_info['price'],
                               stars=hotel_info['stars'],site=hotel_info['site'])
        if user.foto:
            for i in range(int(user.foto_count)):
                link=apidler.get_foto(hotel["id"])[i]["baseUrl"]
                size=apidler.get_foto(hotel["id"])[i]["sizes"][0]["suffix"]
                link_new=re.sub(r'{size}', size, link)
                bot.send_photo(message.chat.id, link_new)
def calendar_func():
    calendar, step=DetailedTelegramCalendar().build()
    bot.send_message(m.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


if __name__ == '__main__':
    bot.infinity_polling()
