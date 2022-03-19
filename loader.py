"""
основной модуль loader.py который погружает все нужное, создает экземпляры если нужны.
В нем должны подгружаться все нужные константы(токены бота, API) инициализироваться класс с ботом TeleBot
"""
import telebot
from loguru import logger
from telebot import types
import os
from dotenv import load_dotenv
from userclass import User
import orm





def env_token(key):
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
         load_dotenv(dotenv_path)
    token=os.getenv(key)
    return token

bot=telebot.TeleBot(env_token('BOT_TOKEN'))


def registration(message: types.Message):
    """
    User initialization, adding to the dictionary user_dict new user
    :param message:message
    :return:
    """
    user=User.reg_user(message.from_user.id)
    user.cmd=message.text
    logger.info('The user {} entered the command {}'.format(message.from_user.id, message.text))
    orm.create_table_guest()
    orm.create_table_hotels()
    bot.send_message(message.chat.id, 'Выберите город для поиска отелей',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'К сожалению, города России не доступны для поиска',
                     reply_markup=types.ReplyKeyboardRemove())




