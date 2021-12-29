'''дочерний rapidapi.py или может как-нибудь иначе? Главное чтобы подходило по смыслу.
В нем создается класс для работы с API и в нем делаются все запросы к API'''
import requests
import json
import re
# from valid import check_sity
headers={
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "a723c1264fmsh34a1941700a33c0p131c96jsncdcfdaa46dcf"
    }

def get_sity_destinationID(sity: str, locale:str):
    url="https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring={"query": sity, "locale": locale, "currency": "RUB"}
    response=requests.request("GET", url, headers=headers, params=querystring, timeout=20)
    result=json.loads(response.text)
    return result['suggestions'][0]['entities']#передаю список из вариантов

def lowprice_func(sity_id: str, count:str, date_in:str, date_out:str, locale:str
                  # low_price:str, top_price:str
                  ):
    url="https://hotels4.p.rapidapi.com/properties/list"
    querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                 "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                 # "priceMin":low_price, "priceMax": top_price,
                 "sortOrder": "PRICE", "locale": locale, "currency": "RUB"}
    response=requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code!=200:
        return "error_server"
    results=json.loads(response.text)
    hotel=results["data"]["body"]["searchResults"]["results"]
    return hotel
def highprice_func(sity_id: str, count:str, date_in:str, date_out:str,  locale:str):
    url="https://hotels4.p.rapidapi.com/properties/list"
    querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                 "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                 "sortOrder": "PRICE_HIGHEST_FIRST", "locale": locale, "currency": "RUB"}
    response=requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code!=200:
        return "error_server"
    results=json.loads(response.text)
    hotel=results["data"]["body"]["searchResults"]["results"]
    return hotel

def bestdeal_func(sity_id: str, count:str, date_in:str, date_out:str, low_price:str, top_price:str,  locale:str):
    # "sortOrder": "PRICE":"DISTANCe_FROM_LANDMARK", "landmarkIds:"City center"
    url="https://hotels4.p.rapidapi.com/properties/list"
    querystring={"destinationId": sity_id, "pageNumber": "1", "pageSize": count,
                 "checkIn": date_in, "checkOut": date_out, "adults1": "1",
                 "priceMin":low_price, "priceMax": top_price,
                 "sortOrder": "PRICE", "locale":locale, "currency": "RUB"}
    response=requests.request("GET", url, headers=headers, params=querystring)
    results=json.loads(response.text)
    if results['result']=='ERROR':
        return "error_server"
    hotel=results["data"]["body"]["searchResults"]["results"]
    return sorted(hotel, key=sort_key)
def get_foto(id:str):
    url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring={"id": id}
    response=requests.request("GET", url, headers=headers, params=querystring)
    results=json.loads(response.text)
    return results["hotelImages"]
def sort_key(hotels):
    return hotels["landmarks"][0]["distance"]

def get_details(id:str, checkin: str, checkout: str, locale):
    url="https://hotels4.p.rapidapi.com/properties/get-details"
    querystring={"id": id, "checkIn": checkin, "checkOut": checkout, "adults1": "1", "currency": "RUB",
                 "locale": locale}
    response=requests.request("GET", url, headers=headers, params=querystring)
    results=json.loads(response.text)
    return results['data']['body']

'''
sity_name='Moscow'
list_sity = get_sity_destinationID(sity_name)
for elem in list_sity:
#     print(elem["caption"])
    if elem["type"]=="CITY" and elem['name'].lower()==sity_name.lower():
        if re.findall(r'>.*<', elem["caption"]):
            print(re.sub(r'<.*>.*</.*>', elem['name'], elem["caption"]))
        else:
            print(elem["caption"])

'''
def get_hotels_data(**kwargs):
    querystring=kwargs
    querystring.update(adults1="1", pageNumber= "1", sortOrder="PRICE", locale = "en_US", currency="USD" )
    url="https://hotels4.p.rapidapi.com/properties/list"
    print(querystring)
    # querystring={"destinationId": get_sity_destinationID(sity), "pageNumber": "1", "pageSize": count,
    #              "checkIn": date_in, "checkOut": date_out, "adults1": "1",
    #              "priceMin":low_price, "priceMax": top_price,
    #              "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}
    response=requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code!=200:
        return "error_server"
    results=json.loads(response.text)
    hotels=results["data"]["body"]["searchResults"]["results"]
    return sorted(hotels, key=sort_key)
def check_locale(city:str):
    city=city.lower()
    if all([True if sym in 'abcdefghighijklmnoprstuvwxyz' else False for sym in city]):
        return 'en_US'
    elif all([True if sym in 'абвгдеёжзиклмнопрстуфхцчшщьыъэюя' else False for sym in city]):
        return 'ru_RU'


