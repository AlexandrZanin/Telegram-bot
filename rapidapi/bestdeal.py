import handlers
import json
from main import bot
from loguru import logger
import re
from rapidapi.apidler import request_to_api, headers
def bestdeal_func(sity_id: str, count:str, date_in:str, date_out:str, low_price:str, top_price:str,  locale:str, currency:str,id):
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
    url="https://hotels4.p.rapidapi.com/properties/list"
    querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                 "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                 "priceMin": low_price, "priceMax": top_price,
                 "sortOrder": "DISTANCE_FROM_LANDMARK",
                 "landmarkIds": "City center", "locale": locale, "currency": currency}
    try:
        response=request_to_api(url, headers, querystring, id)
        pattern='(?<=,)"results":.+(?=,"pagination)'
        find=re.search(pattern, response.text)
        if find:
            results=f'{{{find[0]}}}'
            hotels=json.loads(results)
            logger.info('bestdeal - successful')
            return hotels['results']
        else:
            bot.send_message(id, 'Поиск не дал результатов, для нового поиска нажмите /help')

    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')
    except KeyError as e:
        logger.error('Error {}/highprice'.format(e))
        bot.send_message(id, 'Некорректный ответ, нажмите /help')
