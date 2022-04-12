"""
handlers.py в нем функции для поиска города и вывода результаты поиска
"""
from loader import bot
from userclass import User
from rapidapi import apidler, bestdeal, lowprice, highprice, get_photo
from loguru import logger
from telebot import types
from telegram_bot_calendar import LSTEP
from calendar_my import MyStyleCalendar
from orm import Guest, Hotels_Find
import re
from datetime import date, datetime, timedelta
from valid import check_number_hotels, get_distance, get_price


def check_city(message: types.Message):
    """
    This function creates a InlineKeyboard with the name of cities.
    :param message:
    :return:
    """

    user=User.get_user(message.chat.id)
    user.locale=apidler.check_locale(message.text)
    keyboard=types.InlineKeyboardMarkup()  # наша клавиатура
    try:
        list_sity=apidler.get_sity_destinationid(user.locale, message)
        logger.info('getting list city')
        user.city_name_id.clear()
        question='Ничего не найдено'
        for elem in list_sity:
            if elem["type"] == "CITY":
                question='Уточните'
                temp=elem["caption"].split(',')
                for i in range(len(temp)):
                    if re.search(r'<.*>.*<.*>', temp[i]):
                        del temp[i]
                        break
                if temp[0] == elem['name']:
                    text_button=','.join(temp)
                else:
                    text_button=elem['name'] + ', ' + ','.join(temp)
                user.city_name_id[elem["destinationId"]]=elem['name']
                key=types.InlineKeyboardButton(text=text_button, callback_data=elem["destinationId"])
                keyboard.add(key)
        key1=types.InlineKeyboardButton(text='Ввести другой город', callback_data='again')
        keyboard.add(key1)
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    except (TypeError, KeyError) as e:
        logger.error('{}_check_city'.format(e))


def get_hotels(message: types.Message):
    """
    This function writes user class parameters to the database.
    Receives data from the api.
    Sends search results
    Writes the found hotels to the database
    :param message:
    :return:
    """
    user=User.get_user(message.chat.id)
    wait_message=bot.send_message(message.chat.id, 'Придется немного подождать ⏳')
    new_find=Guest.create(cmd=user.cmd, sity=user.sity, sity_id=user.sity_id,
                          date_in=user.date_in, date_out=user.date_out,
                          low_price=user.low_price, top_price=user.top_price, max_dist=user.max_dist,
                          count_hotels=user.count_hotels, foto=user.foto,
                          foto_count=user.foto_count, user_id=user.id,
                          time_now=datetime.now(), currency=user.currency)
    # .strftime("%m/%d/%Y, %H:%M:%S"
    list_hotels=[]
    if user.cmd == '/lowprice':
        list_hotels=lowprice.lowprice_func(user.sity_id, user.count_hotels, user.date_in,
                                           user.date_out, user.locale, user.currency, message.from_user.id)
    elif user.cmd == '/highprice':
        list_hotels=highprice.highprice_func(user.sity_id, user.count_hotels, user.date_in,
                                             user.date_out, user.locale, user.currency, message.from_user.id)
    elif user.cmd == '/bestdeal':
        list_hotels=bestdeal.bestdeal_func(user.sity_id, user.count_hotels, user.date_in, user.date_out,
                                           user.low_price, user.top_price, user.locale, user.currency,
                                           message.from_user.id)
        try:
            if list_hotels:
                list_hotels=[hotel for hotel in list_hotels if check_dist(hotel,
                                                                          user.max_dist, user.locale)]
        except KeyError:
            logger.info('Дистанция ')
    check_number_hotels(len(list_hotels), user.count_hotels, message.chat.id)
    bot.delete_message(message.chat.id, wait_message.id)
    for hotel in list_hotels:
        hotel_info={}
        try:
            hotel_info['name']=hotel["name"]
        except KeyError:
            logger.error('name not found')
        try:
            if user.locale == 'en_US':
                hotel_info['dist']=str(round(get_distance(hotel["landmarks"][0]["distance"]) * 1.6, 2)) + ' ' + 'км'
            elif user.locale == 'ru_RU':
                hotel_info['dist']=hotel["landmarks"][0]["distance"]
        except KeyError:
            logger.error('distance not found')
            hotel_info['dist']='distance not found'
        try:
            hotel_info['address']=hotel["address"]["streetAddress"] + ', ' + hotel["address"]["locality"] + ', ' + \
                                  hotel["address"]["countryName"]
        except KeyError:
            try:
                details_info=apidler.get_details(hotel['id'], user.date_in, user.date_out, user.locale)
                hotel_info['address']=details_info["propertyDescription"]["address"]["fullAddress"]
            except KeyError:
                logger.error('address not found')
                hotel_info['address']='Адрес отсутствует'
        try:
            hotel_info['price_day']=hotel["ratePlan"]["price"]["current"]
        except KeyError:
            logger.error('price_day not found')
            hotel_info['price_day']='Данных нет'
        try:
            hotel_info['price']=str(int(hotel["ratePlan"]["price"]["exactCurrent"] *
                                        (user.date_out - user.date_in).days))
        except KeyError:
            logger.error('price not found')
            hotel_info['price']='Данных нет'
        hotel_info['stars']=str(hotel["starRating"])
        hotel_info['site']='https://ru.hotels.com/ho' + str(hotel['id'])
        hotel_info['foto']=hotel["optimizedThumbUrls"]["srpDesktop"]
        # "Записываем информацию об отеле в базу данных. "
        hotel_send=Hotels_Find.create(owner=new_find, name=hotel_info['name'], dist=hotel_info['dist'],
                                      addres=hotel_info['address'], price_day=hotel_info['price_day'],
                                      price=hotel_info['price'],
                                      stars=hotel_info['stars'], site=hotel_info['site'], date_in=user.date_in,
                                      date_out=user.date_out, foto=hotel_info['foto'])
        send_info(hotel_send)  # выводим результаты поиска

        if user.foto:
            foto=get_photo.get_foto(hotel["id"])

            for i in range(int(user.foto_count)):
                try:
                    link=foto[i]["baseUrl"]
                    size=foto[i]["sizes"][1]["suffix"]
                    link_new=re.sub(r'{size}', size, link)
                    bot.send_photo(message.chat.id, link_new)
                except IndexError as e:
                    logger.error('get_photos - {}'.format(e))
    bot.send_message(message.from_user.id, "Поиск завершён")


def calendar_func_in(id_):
    """
    Calendar for check-in date: minimum date today, maximum date 31.12.2023
    :param id_: message.id
    :return:
    """
    bot.send_message(id_, 'Введите дату заезда',
                     reply_markup=types.ReplyKeyboardRemove())
    calendar, step=MyStyleCalendar(min_date=date.today(), max_date=date(2023, 12, 31), locale='ru').build()
    bot.send_message(id_,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_func_out(id_):
    """
    Calendar for check-out date: minimum date - check-in date, maximum date 31.12.2023
    :param id_:
    :return:
    """
    bot.send_message(id_, 'Введите дату выезда',
                     reply_markup=types.ReplyKeyboardRemove())
    user=User.get_user(id_)
    calendar, step=MyStyleCalendar(min_date=user.date_in + timedelta(days=+1), max_date=date(2023, 12, 31),
                                   locale='ru').build()
    bot.send_message(id_,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


def get_keyboard(data: str, text: str, message: types.Message):
    """
    This function sends data at the user's request
    Creates InlineKeyboardButton 'Смотреть найденное'.
    Send the search results for this search.
    :param data: 'id' + 'database search id'
    :param text: "{time_now}\n Команда {cmd}\n Город: {city}\n {check-in date}\n {check-out date}"
    :param message: message
    :return:
    """
    # Генерация клавиатуры.
    keyboard=types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Смотреть найденное', callback_data=data))
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)


def check_dist(hotel: dict, max_dist: str, locale: str):
    """
    This function checks whether the distance from the hotel to the city center
    does not exceed the maximum distance that the user entered
    :param hotel: hotel dict with some keys
    :param max_dist: the maximum distance that the user entered
    :param locale: if en_US: then the distance in miles   elif ru_RU: then the distance in kilometers.
    :return: True or False
    """
    dist_to_centr=hotel["landmarks"][0]["distance"]
    if locale == 'en_US':
        dist_to_centr=get_distance(dist_to_centr) * 1.60934
    elif locale == 'ru_RU':
        dist_to_centr=get_distance(dist_to_centr)
    return dist_to_centr < get_distance(max_dist)


def send_info(hotel: Hotels_Find):
    """
    This function sends information about hotel
    :param hotel: orm class Hotels_Find - all found hotels
    :return:
    """
    if (hotel.date_out - hotel.date_in).days % 10 == 1:
        ending='ки'
    else:
        ending='ок'
    user_find=Guest.select().where(Guest.id == hotel.owner).get()  #
    send_info_='🔥 {name}\n🌍 Адрес: {address}\n🚕 Расстояние до центра:' \
               ' {dist}\n💵 Цена за сутки: {price_day}\n💶 Цена за {days} сут{ending}: {price} \n' \
               '⭐ Количество звёзд: {stars}\n' \
               '{site}'.format(name=hotel.name, dist=hotel.dist,
                               address=hotel.addres, price_day=hotel.price_day,
                               price=get_price(hotel.price, user_find.currency),
                               stars=hotel.stars, site=hotel.site,
                               days=(hotel.date_out - hotel.date_in).days, ending=ending)
    bot.send_photo(user_find.user_id, photo=hotel.foto, caption=send_info_)
