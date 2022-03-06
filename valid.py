from loader import bot
def check_number_hotels(len_list_hotels, number, id):
    if len_list_hotels < int(number) and len_list_hotels > 0:
        bot.send_message(id, 'Найдено {} отелей'.format(len_list_hotels))
    elif len_list_hotels == 0:
        bot.send_message(id, 'По вашему запросу не найден ни один отель.'
                                          ' Повторите поиск с другими параметрами')