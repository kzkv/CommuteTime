# -*- coding: UTF-8 -*-
#from __future__ import print_function
import re
from time import time
from datetime import datetime
import json
from pprint import pprint

import mongokit
import requests
from bs4 import BeautifulSoup

from config import MONGODB_URI
import model


db = mongokit.Connection(MONGODB_URI)
db.register([model.Route])


commute_routes = {  # ссылки на мобильные версии карт с маршрутами
    u"Берсеневская—Никулинская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10&rtext=55.740680%2C37.608515~55.669225%2C37.454354",
    u"Никулинская—Берсеневская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10&rtext=55.669225%2C37.454354~55.740680%2C37.608515",
    u"Берсеневская—Микрогород": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10&rtext=55.740680%2C37.608515~55.871353%2C37.326996",
    u"Микрогород—Берсеневская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10&rtext=55.871353%2C37.326996~55.740680%2C37.608515",
    u"Смоленская—Микрогород": u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.747345%2C37.576736~55.871077%2C37.329303",
    u"Микрогород—Смоленская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.871077%2C37.329303~55.747345%2C37.576736",
    u"Смоленская—Никулинская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.747345%2C37.576736~55.669225%2C37.454354",
    u"Никулинская—Смоленская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.669225%2C37.454354~55.747345%2C37.576736",}
jam_maps = {  # ссылки на карты с включенными пробками
    u"Микрогород": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10",
    u"ТТК-запад": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.598%2C55.756&z=11",
    u"Садовое, юго-запад": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.59%2C55.74&z=12",
    u"Юг": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10"}
mobile_maps_url = "http://m.maps.yandex.ru"  # мобильные карты для определения текущего балла пробок
segment_min_length = 1  # минимальная длина сегмента для вывода


with open("route_urls.json") as route_urls_data:
    route_urls = json.load(route_urls_data)

# вывод расстояния и времени в пути
for route_data in route_urls:

    route = model.Route()

    # вывод: timestamp
    #print(datetime.fromtimestamp(time()).strftime(u'%Y-%m-%d %H:%M:%S'))
    route.timestamp = int(time())

    # текущй балл пробок
    soup_content = BeautifulSoup(requests.get(mobile_maps_url).text)
    traffic_source_string = soup_content.find("li", class_="b-traffic").b.string.extract()
    traffic_source_string = re.search(u"(\d+)(.бал*)", traffic_source_string)
    if traffic_source_string:
        traffic_val = int(traffic_source_string.group(1))
        # вывод: пробки
        #print(u"Пробки: {} б.".format(traffic_val))
        route.traffic_val = traffic_val

    #название маршрута
    route.route_name = route_data["routeName"]

    soup_content = BeautifulSoup(requests.get(route_data["routeUrl"]).text)

    # парсинг, поиск дива с информацией о длине пути
    commute_length_source_string = soup_content.find("div", class_="b-route-info__length").strong.string.extract()
    commute_length = int(re.findall("\d+", commute_length_source_string)[0])

    # парсинг, поиск дива с информацией о продолжительности пути
    commute_time_source_string = soup_content.find("div", class_="b-route-info__time").strong.string.extract()
    commute_time_hours = 0
    commute_time_minutes = 0

    # на всякий случай и в часах, и в минутах обрабатывается любой знак десятичного разделителя —
    # в обработку идет только «целая» часть
    # точка («любой символ) вместо \s (пробела) стоит для того, чтобы справиться с юникодными неразрывниками
    commute_time_hours_match = re.search(u"(\d+).*?ч", commute_time_source_string)
    if commute_time_hours_match:
        commute_time_hours = int(commute_time_hours_match.group(1))

    commute_time_minutes_match = re.search(u"(\d+).*?.мин", commute_time_source_string)
    if commute_time_minutes_match:
        commute_time_minutes = int(commute_time_minutes_match.group(1))

    # в часе безальтернативно 60 минут!
    commute_time = commute_time_hours * 60 + commute_time_minutes

    # Вывод ключевых сегментов маршрута
    segment_list = ""
    segment_name_string_prev = ""
    segment_list_source = soup_content("li", class_="b-serp-item")
    for segment_source in segment_list_source:
        # выделяем название сегмента
        segment_name_string = segment_source.find("a", class_="b-serp-item__title-link").string.extract()

        # Отсечение «Налево», «Направо», «Улица» и другого
        clean_pattern = u"Разворот,\s|Направо,\s|Налево,\s|Правее,\s|Левее,\s|Улица\s|улица\s|\sулица|\sпроспект|проспект\s|Проспект |\sшоссе"
        while re.search(clean_pattern, segment_name_string):
            segment_name_string = re.sub(clean_pattern, u"", segment_name_string)

        # Длина сегмента
        segment_length_string = segment_source.find("i", class_="b-serp-item__distance").string.extract()
        if u"км" in segment_length_string:
            segment_length_match = re.search(u"(\d+)(,|)(\d+|)", segment_length_string)
            if segment_length_match:
                # замена разделителя и превращение во float
                segment_length = float(segment_length_match.group(1).replace(',', '.'))

                if segment_length > segment_min_length:  # длина сегмента больше минимальной
                    # разделитель названий сегментов
                    if segment_name_string != segment_name_string_prev:
                        if segment_list != "":
                            segment_list += ", "
                        segment_list += segment_name_string
                        segment_name_string_prev = segment_name_string  # для проверки уникальности

    # вывод: расстояние/время/маршрут
    #print(u'{}: {} км, {} мин ({})'.format(route_name, commute_length, commute_time, segment_list))
    route.commute_length = commute_length
    route.commute_time = commute_time
    route.segment_list = segment_list

    db.

    pprint(route)


""" Отключил из-за отсутствия обработки изображения   # парсинг, поиск изображения карты
    map_node = soup_content.find("img", alt=u"Карта")
    img_url = map_node['src'] if map_node else ""
    # вывод: ссылка на карту
    #print(img_url)
    route.route_map = img_url
    """



""" Временно выключил парсинг дополнительных карт
for map_name, map_url in jam_maps.items():
    soup_content = BeautifulSoup(requests.get(map_url).text)

    # парсинг, поиск изображения карты
    map_node = soup_content.find("img", alt=u"Карта")
    img_url = map_node['src'] if map_node else ""

    # вывод: ссылка на карту
    print(map_name + u": ")
    print(img_url)"""


route_urls_data.close()
