# -*- coding: UTF-8 -*-
#from __future__ import print_function
import re
from time import time
from datetime import datetime
import json

import mongokit
import requests
import pytz
from bs4 import BeautifulSoup

from config import MONGODB_URI
import model


db = mongokit.Connection(MONGODB_URI)
db.register([model.Route])


mobile_maps_url = "http://m.maps.yandex.ru"  # мобильные карты для определения текущего балла пробок
segment_min_length = 1  # минимальная длина сегмента для вывода (в км)


tz = pytz.timezone("Europe/Moscow")


with open("route_urls.json") as route_urls_data:
    route_urls = json.load(route_urls_data)


def route_output(route_data):
    route = db.Route()

    # вывод: timestamp
    route.timestamp = int(time())
    route.timestamp_local = datetime.now(tz).strftime(u'%Y-%m-%d %H:%M:%S')

    # вывод: время дня маршрута
    route.day_time = route_data["dayTime"]

    # текущй балл пробок
    soup_content = BeautifulSoup(requests.get("http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.598%2C55.756&z=11").text)

    traffic_source_string = re.search(u"(\d+)(.бал*)", soup_content.get_text())
    if traffic_source_string:
        traffic_val = int(traffic_source_string.group(1))
        # вывод: пробки
        route.traffic_val = traffic_val

    #название маршрута
    route.route_start = route_data["start"]
    route.route_destination = route_data["destination"]

    soup_content = BeautifulSoup(requests.get(route_data["routeUrl"]).text)

    # парсинг, поиск дива с информацией о длине пути
    commute_length_source_string = soup_content.find("div", class_="b-route-info__length").strong.string.extract()
    commute_length = int(re.findall("\d+", commute_length_source_string)[0])

    # парсинг, поиск дива с информацией о продолжительности пути
    commute_time_source_string = soup_content.find("div", class_="b-route-info__time").strong.string.extract()
    commute_time_hours = 0
    commute_time_minutes = 0

    # время в пути
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

    route.save()


# вывод расстояния и времени в пути
for route_data in route_urls:

    # московское время в часах, %H
    current_hour = datetime.now(tz).hour

    if route_data["dayTime"] == "pm" and (current_hour in (16, 23) or current_hour in (0, 2)):
        route_output(route_data)
    elif route_data["dayTime"] == "am" and current_hour in (6, 15):
        route_output(route_data)
    else:
        pass


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
