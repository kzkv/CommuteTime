# -*- coding: UTF-8 -*-
import os

DATABASE_NAME = "heroku_app18764095"

#MONGODB_URI = "mongodb://localhost:27017/" + DATABASE_NAME

MONGODB_URI = "mongodb://heroku:8Gn-Cpc-Nv3-uuD@ds053128.mongolab.com:53128/heroku_app18764095"
MONGODB_URI = os.getenv('MONGOLAB_URI', MONGODB_URI)

AWS_STORAGE_BUCKET_NAME = "commutetime"
