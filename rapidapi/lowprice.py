from rapidapi.apidler import headers, request_to_api
import json
from main import bot
from loguru import logger
import re
def lowprice_func(sity_id: str, count:str, date_in:str, date_out:str, locale:str, currency:str, id)->list:
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
    url="https://hotels4.p.rapidapi.com/properties/list"
    querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                 "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                 # "priceMin":low_price, "priceMax": top_price,
                 "sortOrder": "PRICE", "locale": locale, "currency": currency}
    try:
        response=request_to_api(url, headers, querystring, id)
        pattern='(?<=,)"results":.+(?=,"pagination)'
        find=re.search(pattern, response.text)
        if find:
            results=f'{{{find[0]}}}'
            hotels=json.loads(results)
            logger.info('lowprice - successful')
            return hotels['results']
        else:
            bot.send_message(id, 'Поиск не дал результатов, для нового поиска нажмите /help')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/lowprice'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')