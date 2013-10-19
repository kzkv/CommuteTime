# -*- coding: UTF-8 -*-

import PySide
# import ghost
import re

commuteRoutes = {
  u"Берсеневская—Никулинская": u"http://maps.yandex.ru/?rtext=55.740680%2C37.608515~55.669225%2C37.454354&sll=37.657654%2C55.740866&sspn=0.714798%2C0.272704&rtm=dtr&source=route&ll=37.657654%2C55.740866&spn=0.714798%2C0.272704&z=11&l=map%2Ctrf&trfm=cur",
  u"Никулинская—Берсеневская": u"http://maps.yandex.ru/?rtext=55.669225%2C37.454354~55.740680%2C37.608515&sll=37.662566%2C55.742543&sspn=0.714798%2C0.272692&rtm=dtr&source=route&ll=37.662566%2C55.742543&spn=0.714798%2C0.272692&z=11&l=map%2Ctrf&trfm=cur",
  u"Берсеневская—Микрогород":  u"http://maps.yandex.ru/?rtext=55.740680%2C37.608515~55.871353%2C37.326996&sll=37.559811%2C55.795737&sspn=0.714798%2C0.272319&rtm=dtr&source=route&ll=37.559811%2C55.795737&spn=0.714798%2C0.272319&z=11&l=map%2Ctrf&trfm=cur",
  u"Микрогород—Берсеневская":  u"http://maps.yandex.ru/?rtext=55.871353%2C37.326996~55.740680%2C37.608515&sll=37.585288%2C55.798019&sspn=0.714798%2C0.272303&rtm=dtr&source=route&ll=37.585288%2C55.798019&spn=0.714798%2C0.272303&z=11&l=map%2Ctrf&trfm=cur"
}

from ghost import Ghost
ghost = Ghost()

pageContent, pageResources = ghost.open(commuteRoutes[u"Берсеневская—Никулинская"])


with open("export.html", "wt") as exportFile:
    exportFile.write(pageContent.encode("UTF-8"))


# print(pageContent)

#print(re.search(u'Ехать', pageContent, flags=0))

# 'Ехать * км'
