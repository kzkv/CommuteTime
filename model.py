# -*- coding: UTF-8 -*-
import time

import mongokit

from config import DATABASE_NAME


class Route(mongokit.Document):
    """Маршрут"""
    __database__ = DATABASE_NAME
    __collection__ = "routes"
    use_dot_notation = True
    skip_validation = True

    structure = {
        "timestamp": int,
        "traffic_val": int,
        "route_name": basestring,
        "commute_length": int,
        "commute_time": int,
        "segment_list": basestring,
        "route_map": basestring,
        "map_start": basestring,
        "map_destination": basestring,
        "day_time": basestring
    }