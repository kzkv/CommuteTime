# -*- coding: UTF-8 -*-
__author__ = 'kzkv'

import mongokit
import model
from datetime import datetime, timedelta
import config

import pytz

import csv

tz = pytz.timezone("Europe/Moscow")
DATE_FORMAT = u"%d.%m.%Y"
OUTPUT_FILE_NAME = "traffic-data.csv"

weekdays = ["1mo", "2tu", "3we", "4th", "5fr", "6sa", "7su"]

db = mongokit.Connection(config.MONGODB_URI)
db.register([model.Route])

writer = csv.writer(open(OUTPUT_FILE_NAME, "w"), delimiter=";", dialect="excel", quoting=csv.QUOTE_MINIMAL)


def get_all_routes(route_start, route_destination):
    # определение POSIX-таймстемпа для дня

    # выбор нужных раутов в список
    day_routes_cursors = db.Route.find({"route_start": route_start,
                                        "route_destination": route_destination}).sort("timestamp",1)

    day_routes = []
    for current_route in day_routes_cursors:
        current_route.timestamp_local = datetime.fromtimestamp(current_route.timestamp).strftime(u'%H:%M')
        day_routes.append(current_route)

    return day_routes


def discard_time_delta(ts):
    #округление времени до ближайших 10 минут
    ts = datetime.fromtimestamp(ts)

    ts = ts - timedelta(minutes=ts.minute % 10,
                        seconds=ts.second,
                        microseconds=ts.microsecond)

    return ts

def make_csv(routes_data):
    #формирование содержимого csv

    for current_route in routes_data:
        traffic_data = ["", "", "", "", "", "", ""]

        route_date = datetime.fromtimestamp(current_route.timestamp).weekday()
        route_rounded_time = discard_time_delta(current_route.timestamp).strftime(u'%H:%M')
        traffic_data[route_date] = str(current_route.traffic_val)
        writer.writerow([route_rounded_time,
                         traffic_data[0],
                         traffic_data[1],
                         traffic_data[2],
                         traffic_data[3],
                         traffic_data[4],
                         traffic_data[5],
                         traffic_data[6],])

writer.writerow(["time", "1mo", "2tu", "3we", "4th", "5fr", "6sa", "7su"])
make_csv(get_all_routes("Микрогород", "Маросейка"))