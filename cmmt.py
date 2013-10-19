# -*- coding: UTF-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import time
import datetime

commuteRoutes = { # ссылки на мобильные версии карт с маршрутами
  u"Берсеневская—Никулинская":
      u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.531599%2C55.705081797743&z=10&rtext=55.740680%2C37.608515~55.669225%2C37.454354",
  u"Никулинская—Берсеневская":
      u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.531599%2C55.705081797743&z=10&rtext=55.669225%2C37.454354~55.740680%2C37.608515",
  u"Берсеневская—Микрогород":
      u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.740680%2C37.608515~55.871353%2C37.326996",
  u"Микрогород—Берсеневская":
      u"http://m.maps.yandex.ru/?l=map%2Ctrf&rtext=55.871353%2C37.326996~55.740680%2C37.608515"}
jamMaps = { # ссылки на карты с включенными пробками
    u"Микрогород":
        u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.457682596679%2C55.82926917756&z=10",
    u"Центр":
        u"http://m.maps.yandex.ru/?l=map%2Ctrf&ll=37.597670999999%2C55.755767999958&z=11"}
mobileMapsURL = "http://m.maps.yandex.ru" # мобильные карты для определения текущего балла пробок
segmentMinLength = 1.5 # минимальная длина сегмента для вывода

# timestamp
print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

# вывод текущего балла пробок
pageContent = requests.get(mobileMapsURL).text
soupContent = BeautifulSoup(pageContent)
trafficSourceString = soupContent.find("li", class_="b-traffic").b.string.extract()
trafficSourceString = re.search(u"(\d+)(.бал*)", trafficSourceString)
if trafficSourceString:
    trafficVal = int (trafficSourceString.group(1))
    print(u"Пробки: " + str(trafficVal) + u" б.")

# вывод расстояния и времени в пути
for key in commuteRoutes.keys():

    #    key = u"Берсеневская—Никулинская"

    pageContent = requests.get(commuteRoutes[key]).text
    soupContent = BeautifulSoup(pageContent)

    commuteLengthSourceString = soupContent.find("div", class_="b-route-info__length").strong.string.extract()
    commuteLength = int(re.findall("\d+", commuteLengthSourceString)[0])

    commuteTimeSourceString = soupContent.find("div", class_="b-route-info__time").strong.string.extract()
    commuteTimeHours = 0
    commuteTimeMinutes = 0

    # на всякий случай и в часах, и в минутах обрабатывается любой знак десятичного разделителя —
    # в обработку идет только «целая» часть
    # точка («любой символ) вместо \s (пробела) стоит для того, чтобы справиться с юникодными неразрывниками
    commuteTimeHoursMatch = re.search(u"(\d+)(.\d+|)(.ч)", commuteTimeSourceString)
    if commuteTimeHoursMatch:
        commuteTimeHours = int(commuteTimeHoursMatch.group(1))

    commuteTimeMinutesMatch = re.search(u"(\d+)(.\d+|)(.мин)", commuteTimeSourceString)
    if commuteTimeMinutesMatch:
        commuteTimeMinutes = int(commuteTimeMinutesMatch.group(1))

    # в часе безальтернативно 60 минут!
    commuteTime = commuteTimeHours*60 + commuteTimeMinutes

    # Вывод ключевых сегментов маршрута
    segmentList = ""
    segmentNameStringPrev = ""
    segmentListSource = soupContent("li", class_="b-serp-item")
    for segmentSourceString in segmentListSource:
        segmentSourceString = BeautifulSoup(str(segmentSourceString))

        # выделяем название сегмента
        segmentNameString = segmentSourceString.find("a", class_="b-serp-item__title-link").string.extract()

        # Отсечение «Налево», «Направо», «Улица» и другого
        cleanPattern = u"Разворот,\s|Направо,\s|Налево,\s|Правее,\s|Левее,\s|Улица[\s|]|улица\s|\sулица|\sпроспект|проспект\s|\sшоссе"
        while re.search(cleanPattern, segmentNameString):
            segmentNameString = re.sub(cleanPattern, u"", segmentNameString)

        # Длина сегмента
        segmentLengthString = segmentSourceString.find("i", class_="b-serp-item__distance").string.extract()
        if re.search(u"км", segmentLengthString):
            segmentLengthMatch = re.search(u"(\d+),(\d+)", segmentLengthString)
            if segmentLengthMatch:
                # замена разделителя и превращение во float
                segmentLength = float(segmentLengthMatch.group(1)+"."+segmentLengthMatch.group(2))

                if segmentLength > segmentMinLength: # длина сегмента больше минимальной
                    # разделитель названий сегментов

                    if segmentNameString != segmentNameStringPrev:
                        if segmentList != "": segmentList += ", "
                        segmentList += segmentNameString
                        segmentNameStringPrev = segmentNameString # для проверки уникальности

    # вывод
    print(key + u": " +
          str(commuteLength) + u" км, " +
          str(commuteTime) + u" мин") + u" (" + segmentList + u")"




#print(soupContent.prettify())

#with open("export.html", "wt") as exportFile:
#    exportFile.write(pageContent.encode("UTF-8"))

# print(pageContent)