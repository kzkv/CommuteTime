# -*- coding: UTF-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import time
import datetime

commute_routes = {  # ссылки на мобильные версии карт с маршрутами
    u"Берсеневская—Никулинская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10&rtext=55.740680%2C37.608515~55.669225%2C37.454354",
    u"Никулинская—Берсеневская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10&rtext=55.669225%2C37.454354~55.740680%2C37.608515",
    u"Берсеневская—Микрогород": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10&rtext=55.740680%2C37.608515~55.871353%2C37.326996",
    u"Микрогород—Берсеневская": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10&rtext=55.871353%2C37.326996~55.740680%2C37.608515"}
jam_maps = {  # ссылки на карты с включенными пробками
    u"Микрогород": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.48%2C55.80&z=10",
    u"Центр": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.598%2C55.756&z=11",
    u"Юг": u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.50%2C55.71&z=10"}
mobile_maps_url = "http://m.maps.yandex.ru"  # мобильные карты для определения текущего балла пробок
segment_min_length = 1  # минимальная длина сегмента для вывода

# вывод: timestamp
print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

# текущй балл пробок
soup_content = BeautifulSoup(requests.get(mobile_maps_url).text)
traffic_source_string = soup_content.find("li", class_="b-traffic").b.string.extract()
traffic_source_string = re.search(u"(\d+)(.бал*)", traffic_source_string)
if traffic_source_string:
    traffic_val = int(traffic_source_string.group(1))
    # вывод: пробки
    print(u"Пробки: " + str(traffic_val) + u" б.")

# вывод расстояния и времени в пути
for key in commute_routes.keys():

    soup_content = BeautifulSoup(requests.get(commute_routes[key]).text)

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
    commute_time_hours_match = re.search(u"(\d+)(.\d+|)(.ч)", commute_time_source_string)
    if commute_time_hours_match:
        commute_time_hours = int(commute_time_hours_match.group(1))

    commute_time_minutes_match = re.search(u"(\d+)(.\d+|)(.мин)", commute_time_source_string)
    if commute_time_minutes_match:
        commute_time_minutes = int(commute_time_minutes_match.group(1))

    # в часе безальтернативно 60 минут!
    commute_time = commute_time_hours * 60 + commute_time_minutes

    # Вывод ключевых сегментов маршрута
    segment_list = ""
    segment_name_string_prev = ""
    segment_list_source = soup_content("li", class_="b-serp-item")
    for segment_source_string in segment_list_source:
        segment_source_string = BeautifulSoup(str(segment_source_string))

        # выделяем название сегмента
        segment_name_string = segment_source_string.find("a", class_="b-serp-item__title-link").string.extract()

        # Отсечение «Налево», «Направо», «Улица» и другого
        clean_pattern = u"Разворот,\s|Направо,\s|Налево,\s|Правее,\s|Левее,\s|Улица\s|улица\s|\sулица|\sпроспект|проспект\s|\sшоссе"
        while re.search(clean_pattern, segment_name_string):
            segment_name_string = re.sub(clean_pattern, u"", segment_name_string)

        # Длина сегмента
        segment_length_string = segment_source_string.find("i", class_="b-serp-item__distance").string.extract()
        if re.search(u"км", segment_length_string):
            segment_length_match = re.search(u"(\d+)(,|)(\d+|)", segment_length_string)
            if segment_length_match:
                # замена разделителя и превращение во float
                segment_length = float(segment_length_match.group(1) + "." + segment_length_match.group(3))

                if segment_length > segment_min_length:  # длина сегмента больше минимальной
                    # разделитель названий сегментов

                    if segment_name_string != segment_name_string_prev:
                        if segment_list != "":
                            segment_list += ", "
                        segment_list += segment_name_string
                        segment_name_string_prev = segment_name_string  # для проверки уникальности

    # вывод: расстояние/время/маршрут
    print(key + u": " +
          str(commute_length) + u" км, " +
          str(commute_time) + u" мин") + u" (" + segment_list + u")"

    # парсинг, поиск изображения карты
    if soup_content.find("img", alt=u"Карта"):
        img_url = soup_content.find("img", alt=u"Карта")['src']
    else:
        img_url = ""

    # вывод: ссылка на карту
    print(img_url)


for key in jam_maps.keys():
    soup_content = BeautifulSoup(requests.get(jam_maps[key]).text)

    # парсинг, поиск изображения карты
    if soup_content.find("img", alt=u"Карта"):
        img_url = soup_content.find("img", alt=u"Карта")['src']
    else:
        img_url = "n/a"

    # вывод: ссылка на карту
    print(key + u": ")
    print(img_url)
