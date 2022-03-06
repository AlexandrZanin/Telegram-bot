'''
дочерний handlers.py в нем объявляются все кастомные хендлеры -
получение города, количества отелей и прочее
'''
from loader import bot
from userclass import User
from rapidapi import apidler, bestdeal, lowprice, highprice, get_photo
from loguru import logger
from telebot import types
from telegram_bot_calendar import LSTEP
from calendar_my import MyStyleCalendar
import orm
import re
from datetime import date, datetime
from valid import check_number_hotels

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
        list_sity=apidler.get_sity_destinationID(user.locale, message)
        logger.info('geting list city')
        user.city_name_id.clear()
        question='Ничего не найдено'
        for elem in list_sity:
            if elem["type"] == "CITY":
                question='Уточните'
                # if re.findall(r'>.*<', elem["caption"]):
                #      text_button=re.sub(r'<.*>.*</.*>', elem['name'], elem["caption"])
                # else:
                # text_button=re.sub(r'.*</.*>,', elem['name'], elem["caption"])
                # text_button=elem["caption"]
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
    bot.send_message(message.chat.id, 'Придется немного подождать ⏳')
    new_find=orm.Guest.create(cmd=user.cmd, sity=user.sity, sity_id=user.sity_id,
                              date_in=user.date_in, date_out=user.date_out,
                              low_price=user.low_price, top_price=user.top_price, max_dist=user.max_dist,
                              count_hotels=user.count_hotels, foto=user.foto,
                              foto_count=user.foto_count, user_id=user.id,
                              time_now=datetime.now())
    # .strftime("%m/%d/%Y, %H:%M:%S"
    if user.cmd == '/lowprice':
        list_hotels=lowprice.lowprice_func(user.sity_id, user.count_hotels, user.date_in,
                                          user.date_out, user.locale, user.currency, message.from_user.id)
    elif user.cmd == '/highprice':
        list_hotels=highprice.highprice_func(user.sity_id, user.count_hotels, user.date_in,
                                           user.date_out, user.locale, user.currency, message.from_user.id)
    elif user.cmd == '/bestdeal':
        list_hotels=bestdeal.bestdeal_func(user.sity_id, user.count_hotels, user.date_in, user.date_out,
                                          user.low_price, user.top_price, user.locale, user.currency, message.from_user.id)
        # try:
        #     list_hotels=[hotel for hotel in list_hotels if check_dist(hotel["landmarks"][0]["distance"],
        #                                                               user.max_dist, user.locale)]
        # except:
        #     logger.info('Какая-то фигня')
    check_number_hotels(len(list_hotels), user.count_hotels, message.chat.id)
    for hotel in list_hotels:
        hotel_info={}
        try:
            hotel_info['name']=hotel["name"]
        except:
            logger.error('name not found')
        try:
            hotel_info['dist']=hotel["landmarks"][0]["distance"]
        except:
            logger.error('distance not found')
        try:
            hotel_info['addres']=hotel["address"]["streetAddress"]+', '+hotel["address"]["locality"]+', '+hotel["address"]["countryName"]
        except KeyError:
            details_info=apidler.get_details(hotel['id'], user.date_in, user.date_out, user.locale)
            hotel_info['addres']=details_info["propertyDescription"]["address"]["fullAddress"]  # может отсутствовать информация
        except KeyError:
            logger.error('addres not found')
            hotel_info['addres']='Адрес отсутствует'
        hotel_info['price_day']=hotel["ratePlan"]["price"]["current"]

        price_current=int(re.sub(r',', ".", re.search(r'\d+[,]*\d*', hotel["ratePlan"]["price"]["current"])[0]))
        hotel_info['price']=str(price_current * (user.date_out - user.date_in).days)
        hotel_info['stars']=str(hotel["starRating"])
        hotel_info['site']='https://ru.hotels.com/ho' + str(hotel['id'])
        send_info='🔥 {name}\n🌍 Адрес: {addres}\n🚕 Расстояние до центра:' \
                  ' {dist}\n💵 Цена за сутки: {price_day}\n💵 Цена  за {days} суток: {price} {currency}\n'\
                  '⭐ Количество звёзд: {stars}\n' \
                  '{site}'.format(name=hotel_info['name'], dist=hotel_info['dist'],
                                  addres=hotel_info['addres'], price_day=hotel_info['price_day'], price=hotel_info['price'],
                                  stars=hotel_info['stars'], site=hotel_info['site'], days=(user.date_out - user.date_in).days,
                                  currency=user.currency)
        bot.send_message(message.chat.id, send_info)
        orm.Hotels_find.create(owner=new_find, name=hotel_info['name'], dist=hotel_info['dist'],
                               addres=hotel_info['addres'], price=hotel_info['price'],
                               stars=hotel_info['stars'], site=hotel_info['site'])
        if user.foto:
            foto=get_photo.get_foto(hotel["id"])
            for i in range(int(user.foto_count)):
                try:
                    link=foto[i]["baseUrl"]
                    size=foto[i]["sizes"][1]["suffix"]
                    link_new=re.sub(r'{size}', size, link)
                    bot.send_photo(message.chat.id, link_new)
                except IndexError as e:
                    logger.error('get_fotos - {}'.format(e))

    # except Exception:
    #     logger.error('Some data is not received')
    #     bot.send_message(message.chat.id, "Не удалось найти данные, нажмите /help")


def calendar_func_in(id):
    """
    Calendar for check-in date: minimum date today, maximum date 31.12.2023
    :param id:
    :return:
    """
    bot.send_message(id, 'Введите дату заезда',
                     reply_markup=types.ReplyKeyboardRemove())
    calendar, step=MyStyleCalendar(min_date=date.today(), max_date=date(2023, 12, 31), locale='ru').build()
    bot.send_message(id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_func_out(id):
    """
    Calendar for check-out date: minimum date - check-in date, maximum date 31.12.2023
    :param id:
    :return:
    """
    bot.send_message(id, 'Введите дату выезда',
                     reply_markup=types.ReplyKeyboardRemove())
    user=User.get_user(id)
    calendar, step=MyStyleCalendar(min_date=user.date_in, max_date=date(2023, 12, 31), locale='ru').build()
    bot.send_message(id,
                     f"Select {LSTEP[step]}",
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


def check_dist(dist_to_centr: str, max_dist: str, locale: str):
    """
    This function checks whether the distance from the hotel to the city center
    does not exceed the maximum distance that the user entered
    :param dist_to_centr: distance from the hotel to the city center from api
    :param max_dist: the maximum distance that the user entered
    :param locale: if en_US: then the distance in miles   elif ru_RU: then the distance in kilometers.
    :return: True or False
    """
    if locale == 'en_US':
        dist_to_centr=round(float(re.findall('\d+[.,]*\d*', dist_to_centr)[0]) * 1.6, 2)
    elif locale == 'ru_RU':
        dist_to_centr=round(float(re.findall('\d+[.,]*\d*', dist_to_centr)[0]), 2)
    max_dist=round(float(re.findall('\d+[.,]*\d*', max_dist)[0]), 2)
    return dist_to_centr < max_dist
