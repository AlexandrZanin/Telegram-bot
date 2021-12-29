'''main.py основной скрипт который запускает работу,
в нем должны быть нужные импорты и функции которые используют декораторы message_handler и подобные.
'''
import os
import telebot
from dotenv import load_dotenv


def env_token():
    dotenv_path=os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    token=os.getenv('BOT_TOKEN')
    return token


bot=telebot.TeleBot(env_token())


