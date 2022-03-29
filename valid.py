"""
Включает в себя функции проверки.
"""
from loader import bot
import re
def check_number_hotels(len_list_hotels: int, number, id):
    """
    This function check the number of hotels
    :param len_list_hotels: the number of hotels
    :param number: the parameter number of hotels, set by the user
    :param id: message.chat.id
    :return:
    """
    if len_list_hotels < int(number) and len_list_hotels > 0:
        bot.send_message(id, 'Найдено отелей: {}'.format(len_list_hotels))
    elif len_list_hotels == 0:
        bot.send_message(id, 'По вашему запросу не найден ни один отель.'
                                          ' Повторите поиск с другими параметрами')

def get_distance(distance:str):
    """
    This function gets a string, sets a float.
    :param distance: str
    :return: float
    For ex.:"0.7 miles"->0.7
    """
    return float(re.sub(r',',".",re.findall('\d+[.,]*\d*', distance)[0]))

def get_price(price:str):
    d=price[::-1]
    n=3
    chunks=[d[i:i + n][::-1] for i in range(0, len(d), n)]
    chunks.reverse()
    return ','.join(chunks)
