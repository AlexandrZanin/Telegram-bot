"""
дочерний rapidapi.py или может как-нибудь иначе? Главное чтобы подходило по смыслу.
В нем создается класс для работы с API и в нем делаются все запросы к API
"""
import requests
import json
from main import bot
from telebot import types
from loguru import logger
import os
from dotenv import load_dotenv

def headers_api():
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    x_rapidapi_key=os.getenv('x-rapidapi-key')
    return x_rapidapi_key
headers={
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key':headers_api()}

def get_sity_destinationID(locale:str, message:types.Message):
    """
    This function gets a list of found cities from the api
    :param locale: ru_RU or en_US
    :param message: message
    :return: list of cities found
    """
    sity=message.text
    try:
        url="https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring={"query": sity, "locale": locale, "currency": "RUB"}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code!=200:
            logger.error('server error status!=200')
            bot.send_message(message.from_user.id, 'Ошибка в соединение с сервером')
        else:
            logger.info('get_sity_id {} - successful'.format(sity))
            result=json.loads(response.text)
            return result['suggestions'][0]['entities']#передаю список из вариантов
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(message.from_user.id, 'Ошибка в соединение')
    except TimeoutError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(message.from_user.id, 'время истекло')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(message.from_user.id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/get_sity_destinationID'.format(e))
        bot.send_message(message.from_user.id, 'Некорректный ответ, нажмите /help')

def lowprice_func(sity_id: str, count:str, date_in:str, date_out:str, locale:str, id)->list:
    """
    This function finds the cheapest hotels.
    Hotels are sorted by price.
    :param sity_id: city id
    :param count: how many hotels to show
    :param date_in: check-in date to the hotel
    :param date_out: check-out date to the hotel
    :param locale: en_US or ru_RU
    :param id: user id
    :return list of hotels:
    """
    try:
        url="https://hotels4.p.rapidapi.com/properties/list"
        querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                     "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                     # "priceMin":low_price, "priceMax": top_price,
                     "sortOrder": "PRICE", "locale": locale, "currency": "RUB"}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code!=200:
            logger.error('server error status!=200')
        else:
            results=json.loads(response.text)
            hotel=results["data"]["body"]["searchResults"]["results"]
            logger.info('lowprice - successful')
            return hotel
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Ошибка в соединение')
    except TimeoutError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Время запроса истекло')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/lowprice'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')
def highprice_func(sity_id: str, count:str, date_in:str, date_out:str,  locale:str, id):
    """
        This function finds the most expensive hotels.
        Hotels are sorted by price, first expensive
        :param sity_id: city id
        :param count: how many hotels to show
        :param date_in: check-in date to the hotel
        :param date_out: check-out date to the hotel
        :param locale: en_US or ru_RU
        :param id: user id
        :return list of hotels:
        """
    try:
        url="https://hotels4.p.rapidapi.com/properties/list"
        querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                     "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                     "sortOrder": "PRICE_HIGHEST_FIRST", "locale": locale, "currency": "RUB"}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=15)
        if response.status_code!=200:
            logger.error('server error status!=200')
        else:
            results=json.loads(response.text)
            hotel=results["data"]["body"]["searchResults"]["results"]
            logger.info('highprice - successful')
            return hotel
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Ошибка в соединение')
    except TimeoutError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'время истекло')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/highprice'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')

def bestdeal_func(sity_id: str, count:str, date_in:str, date_out:str, low_price:str, top_price:str,  locale:str, id):
    """
            This function searches for hotels in the price range and
            no more than the set distance from the center .
            Hotels are sorted by price, first expensive
            :param sity_id: city id
            :param count: how many hotels to show
            :param date_in: check-in date to the hotel
            :param date_out: check-out date to the hotel
            :param low_price:lower price limits
            :param top_price: upper price limits
            :param locale: en_US or ru_RU
            :param id: user id
            :return list of hotels:
            """
    try:
        url="https://hotels4.p.rapidapi.com/properties/list"
        querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                     "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                     "priceMin":low_price, "priceMax": top_price,
                     "sortOrder": "DISTANCE_FROM_LANDMARK",
                     "landmarkIds":"City center", "locale":locale, "currency": "RUB"}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code!=200:
            logger.error('server error status!=200')
        else:
            results=json.loads(response.text)
            hotel=results["data"]["body"]["searchResults"]["results"]
            logger.info('bestdeal - successful')
            return hotel
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Ошибка в соединение')
    except TimeoutError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'время истекло')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/bestdeal'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')
    except requests.exceptions.ReadTimeout as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')

def get_foto(id:str):
    """
    This function receives photos from the api
    :param id: hotel id
    :return: list of foto
    """
    try:
        url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring={"id": id}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code!=200:
            logger.error('server error status!=200')
        else:
            results=json.loads(response.text)
            logger.info('get_foto - successful')
            return results["hotelImages"]
    except KeyError as e:
        logger.error('Error {}/get_foto'.format(e))
        bot.send_message(id, 'Некорректный ответ, при запросе фото')
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Ошибка в соединение')
    except requests.Timeout as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'время истекло')

def get_details(id:str, checkin: str, checkout: str, locale):
    """

    :param id: hotel id
    :param checkin: check-in date to the hotel
    :param checkout: check-out date to the hotel
    :param locale: en_US or ru_RU
    :return:
    """
    try:
        url="https://hotels4.p.rapidapi.com/properties/get-details"
        querystring={"id": id, "checkIn": checkin, "checkOut": checkout, "adults1": "1", "currency": "RUB",
                     "locale": locale}
        response=requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        if response.status_code!=200:
            logger.error('server error status!=200')
            bot.send_message(id, 'Ошибка в соединение. Нажмите \help')
        else:
            results=json.loads(response.text)
            logger.info('get_details - successful')
            return results['data']['body']
    except KeyError as e:
        logger.error('Error {}/get_details'.format(e))
        bot.send_message(id, 'Некорректный ответ, при запросе фото')
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Ошибка в соединение')

'''

#не используется
def get_hotels_data(**kwargs):
    querystring=kwargs
    querystring.update(adults1="1", pageNumber= "1", sortOrder="PRICE" )
    url="https://hotels4.p.rapidapi.com/properties/list"
    print(querystring)
    # querystring={"destinationId": get_sity_destinationID(sity), "pageNumber": "1", "pageSize": count,
    #              "checkIn": date_in, "checkOut": date_out, "adults1": "1",
    #              "priceMin":low_price, "priceMax": top_price,
    #              "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}
    response=requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code!=200:
       print("error_server")
    results=json.loads(response.text)
    hotels=results["data"]["body"]["searchResults"]["results"]
    return sorted(hotels)
    '''
def check_locale(city:str):
    city=city.lower()
    if all([True if sym in 'abcdefghighijklmnoprstuvwxyz- ' else False for sym in city]):
        return 'en_US'
    elif all([True if sym in 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя- ' else False for sym in city]):
        return 'ru_RU'
    else:
        return 'en_US'
