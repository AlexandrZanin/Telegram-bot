"""
дочерний rapidapi.py или может как-нибудь иначе? Главное чтобы подходило по смыслу.
В нем создается класс для работы с API и в нем делаются все запросы к API
"""
import requests
import json
from main import bot
from telebot import types
from loguru import logger
from loader import env_token
import re

headers={
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key':env_token('x-rapidapi-key')}
def request_to_api(url, headers, querystring, user_id):
    try:
        response = requests.request("GET",url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            return response
        else:
            bot.send_message(user_id, 'Ошибка в соединение с сервером')
            logger.info('status code - {}'.format(response.status_code ))
    except ConnectionError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(user_id, 'Ошибка в соединение')
    except TimeoutError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(user_id, 'время истекло')

def get_sity_destinationID(locale:str, message:types.Message):
    """
    This function gets a list of found cities from the api
    :param locale: ru_RU or en_US
    :param message: message
    :return: list of cities found
    """
    sity=message.text
    url="https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring={"query": sity, "locale": locale, "currency": "RUB"}
    try:
        response=request_to_api(url, headers, querystring, message.from_user.id)
        pattern=r'(?<="CITY_GROUP",).+?[\]]'
        find=re.search(pattern, response.text)
        if find:
            result=json.loads(f"{{{find[0]}}}")
            logger.info('get_city_destinationID - successful')
            return result['entities']
        else:
            logger.info('response city error')
                # result['suggestions'][0]['entities']#передаю список из вариантов
    except json.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(message.from_user.id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/get_sity_destinationID'.format(e))
        bot.send_message(message.from_user.id, 'Некорректный ответ, нажмите /help')

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

def check_locale(city:str):
    city=city.lower()
    if all([True if sym in 'abcdefghighijklmnoprstuvwxyz- ' else False for sym in city]):
        return 'en_US'
    elif all([True if sym in 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя- ' else False for sym in city]):
        return 'ru_RU'
    else:
        return 'en_US'
