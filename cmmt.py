# -*- coding: UTF-8 -*-
#from __future__ import print_function
import re
import json
from time import time
from datetime import datetime
import urllib2
import StringIO

import mongokit
import requests
import pytz
from bs4 import BeautifulSoup
import boto
from boto.s3.key import Key

import config
import model

import pprint


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


db = mongokit.Connection(config.MONGODB_URI)
db.register([model.Route])


mobile_maps_url = "http://m.maps.yandex.ru"  # мобильные карты для определения текущего балла пробок
segment_min_length = 0.5  # минимальная длина сегмента для вывода (в км)
am_range = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
pm_range = [16, 17, 18, 19, 20, 21, 22, 23, 0, 1]

tz = pytz.timezone("Europe/Moscow")


def get_map_url(soup_content):
    """вывод ссылки на изображение"""
    map_node = soup_content.find("img", alt=u"Карта")
    img_url = map_node['src'] if map_node else ""
    return img_url


def upload_image(image_url, image_name):
    """аплоад изображения"""
    try:
        # соединение с S3 bucket
        connection = boto.connect_s3()
        bucket = connection.get_bucket(config.AWS_STORAGE_BUCKET_NAME)
        key = Key(bucket)

        # присвоение имени файла
        key.key = str(int(time())) + "-" + image_name + ".png"

        # чтение
        file_object = urllib2.urlopen(image_url)
        file_data = StringIO.StringIO(file_object.read())

        # запись
        key.content_type = "image/png"
        key.set_contents_from_file(file_data)

        # права на чтение
        key.make_public()

        result_url = key.generate_url(0, expires_in_absolute=True, force_http=True, query_auth=False)
        return result_url

    except Exception, e:
        return e


def route_output(route_data):
    """сбор инфо и вывод объекта в базу"""

    # забираем Beautifulsoup-объекты
    route_soup_content = BeautifulSoup(requests.get(route_data["routeUrl"]).text)
    start_soup_content = BeautifulSoup(requests.get(route_data["startMapUrl"]).text)
    desti_soup_content = BeautifulSoup(requests.get(route_data["destinationMapUrl"]).text)

    # объект БД
    route = db.Route()

    # вывод: timestamp
    route.timestamp = int(time())
    route.timestamp_local = datetime.now(tz).strftime(u'%Y-%m-%d %H:%M:%S')

    # вывод: время дня маршрута
    route.day_time = route_data["dayTime"]

    # карты
    route_map_url = get_map_url(route_soup_content)
    if route_map_url != "":
        route.route_map = upload_image(route_map_url, "route")

    start_map_url = get_map_url(start_soup_content)
    if start_map_url != "":
        route.start_map = upload_image(start_map_url, "start")

    desti_map_url = get_map_url(desti_soup_content)
    if desti_map_url != "":
        route.desti_map = upload_image(desti_map_url, "desti")

    # текущй балл пробок
    traffic_source_string = re.search(u"(\d+)(.бал*)", start_soup_content.get_text())
    if traffic_source_string:
        traffic_val = int(traffic_source_string.group(1))
        # вывод: пробки
        route.traffic_val = traffic_val

    #название маршрута
    route.route_start = route_data["start"]
    route.route_destination = route_data["destination"]

    # парсинг, поиск дива с информацией о длине пути
    commute_length_source_string = route_soup_content.find("div", class_="b-route-info__length").strong.string.extract()
    commute_length = int(re.findall("\d+", commute_length_source_string)[0])

    # парсинг, поиск дива с информацией о продолжительности пути
    commute_time_source_string = route_soup_content.find("div", class_="b-route-info__time").strong.string.extract()
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
    segment_list_source = route_soup_content("li", class_="b-serp-item")
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

    #MyPrettyPrinter().pprint(route)
    route.save()


# чтение конфига маршрутов
with open("route_urls.json") as route_urls_data:
    route_urls = json.load(route_urls_data)

# вывод расстояния и времени в пути
for route_data in route_urls:

    # московское время в часах, %H
    current_hour = datetime.now(tz).hour

    if route_data["dayTime"] == "pm" and current_hour in pm_range:
        route_output(route_data)
    elif route_data["dayTime"] == "am" and current_hour in am_range:
        route_output(route_data)
    else:
        pass
