from rapidapi.apidler import headers, request_to_api
import json
from main import bot
from loguru import logger
import re
def get_foto(id:str):
    """
    This function receives photos from the api
    :param id: hotel id
    :return: list of foto
    """
    url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring={"id": id}
    try:
        response=request_to_api(url, headers, querystring, id)
        foto=json.loads(response.text)
        return foto["hotelImages"]
    except KeyError as e:
        logger.error('Error {}/get_foto'.format(e))
        bot.send_message(id, 'Некорректный ответ, при запросе фото')
    except json.decoder.JSONDecodeError as e:
        logger.error('Api connection error {}'.format(e))
        bot.send_message(id, 'Некорректный ответ')

