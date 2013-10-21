# -*- coding: UTF-8 -*-
import re

reg = (u"54 мин",
       u"3?234 мин",
       u"1 ч 30 мин")

for reg in reg:
    commuteTimeHours = 0
    commuteTimeMinutes = 0

    # на всякий случай и в часах, и в минутах обрабатывается любой знак десятичного разделителя —
    # в обработку идет только «целая» часть
    commuteTimeHoursMatch = re.search(u"(\d+)(.\d+|)(.ч)", reg)
    if commuteTimeHoursMatch:
        commuteTimeHours = int(commuteTimeHoursMatch.group(1))

    commuteTimeMinutesMatch = re.search(u"(\d+)(.\d+|)(.мин)", reg)
    if commuteTimeMinutesMatch:
        commuteTimeMinutes = int(commuteTimeMinutesMatch.group(1))

    # в часе безальтернативно 60 минут
    commuteTime = commuteTimeHours * 60 + commuteTimeMinutes
    print (commuteTime)
