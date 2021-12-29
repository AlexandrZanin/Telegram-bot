'''
дочерний handlers.py в нем объявляются все кастомные хендлеры -
получение города, количества отелей и прочее
'''
from main import bot
from telebot import types
from apidler import Hotelsapi
class Handlers:
    def __init__(self, bot, message):
        super().__init__(bot)
        self.message=message
        self.sity=None
        self.number_of_hotels=1
    def get_lowprice(self):
        self.get_sity()
    def get_sity(self):
        self.bot.send_message(self.message.chat.id, 'Выберите город для поиска отелей',
                                  reply_markup=types.ReplyKeyboardRemove())
        self.bot.register_next_step_handler(self.message, self.get_number_hotels())

    def get_number_hotels(self):
        self.sity=self.message.text
        self.bot.send_message(self.message.chat.id, 'Сколько нужно штук?',
                              reply_markup=types.ReplyKeyboardRemove())
        self.bot.register_next_step_handler(self.message, self.send_lowprice())
    def send_lowprice(self):
        self.number_of_hotels=self.message.text
        for hotel in Hotelsapi.lowprice_func(self.sity, self.number_of_hotels):
            self.bot.send_message(self.message.chat.id, hotel)
from loader import telegram_bot

def choose_the_city(message):
    # Какая либо логика, получение города из API например
    data_city = rapidapi.HotelsApi(message.text)
    result = data_city.query_city(message) # Сделали запрос и получили ответ
    telegram_bot.send_message(message.chat.id, 'text')