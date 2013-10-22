# -*- coding: UTF-8 -*-
import os

DATABASE_NAME = "commute_time"

MONGODB_URI = "mongodb://localhost:27017/" + DATABASE_NAME
MONGODB_URI = os.getenv('MONGOLAB_URI', MONGODB_URI)
