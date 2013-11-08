# -*- coding: UTF-8 -*-
__author__ = 'kzkv'

from flask import Flask, render_template

import mongokit
import model
import time
from datetime import datetime
import pytz

import config

from prettyprinter import pretty_print

tz = pytz.timezone("Europe/Moscow")

db = mongokit.Connection(config.MONGODB_URI)
db.register([model.Route])

app = Flask(__name__)

@app.route('/')


def output():
    # !!! переменные из параметров
    given_date = datetime.today()
    route_from = u"Микрогород"
    route_to = u"Маросейка"

    # расчет маршрутов
    day_routes_forth = get_day_routes(given_date, route_from, route_to)
    day_routes_back = get_day_routes(given_date, route_to, route_from)

    # рендер шаблона
    return render_template("layout.html",
                           given_date=given_date.strftime(u"%d.%m.%Y"),
                           day_routes_forth=day_routes_forth,
                           day_routes_back=day_routes_back,
                           route_from=route_from,
                           route_to=route_to)


def get_day_routes(given_date, route_start, route_destination):
    # определение POSIX-таймстемпа для дня
    day_start = int(datetime(given_date.year, given_date.month, given_date.day, 5, 0, 0, 0, tz).strftime("%s"))
    day_end = int(datetime(given_date.year, given_date.month, given_date.day+1, 3, 0, 0, 0, tz).strftime("%s"))

    # выбор нужных раутов в список
    day_routes_cursors = db.Route.find({"timestamp": {"$gt": day_start, "$lt": day_end},
                                        "route_start": route_start,
                                        "route_destination": route_destination}).sort("timestamp",1)

    day_routes = []
    for current_route in day_routes_cursors:
        current_route.timestamp_local = datetime.fromtimestamp(current_route.timestamp).strftime(u'%H:%M')
        day_routes.append(current_route)

    return day_routes


#day_routes = get_day_routes(datetime.today(), u"Маросейка", u"Микрогород")
#pretty_print(list(day_routes))


if __name__ == '__main__':
    app.run()


