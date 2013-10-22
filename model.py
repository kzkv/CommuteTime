# -*- coding: UTF-8 -*-
import time

import mongokit

from config import DATABASE_NAME


class Map(mongokit.Document):
    __database__ = DATABASE_NAME
    __collection__ = "maps"
    use_dot_notation = True
    skip_validation = True

    structure = {
        "map_name": basestring,
        "map_url": basestring
    }


class Route(mongokit.Document):
    __database__ = DATABASE_NAME
    __collection__ = "routes"
    use_dot_notation = True
    skip_validation = True

    structure = {
        "route_name": basestring,
        "commute_length": int,
        "commute_time": int,
        "segment_list": basestring,
        "map": Map
    }


class Commute(mongokit.Document):
    __database__ = DATABASE_NAME
    __collection__ = "commutes"
    use_dot_notation = True
    skip_validation = True

    structure = {
        "traffic_val": int,
        "routes": [Route],
        "maps": [Map],
        "timestamp": int,
    }

    default_values = {
        "timestamp": lambda: int(time.time())
    }
