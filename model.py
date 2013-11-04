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
        "timestamp_local": basestring,
        "traffic_val": int,
        "route_name": basestring,
        "route_start": basestring,
        "route_destination": basestring,
        "commute_length": int,
        "commute_time": int,
        "segment_list": basestring,
        "route_map": basestring,
        "start_map": basestring,
        "desti_map": basestring,
        "day_time": basestring
    }
