#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage metrics JSON API. Simple web.py based API to a
PostgreSQL database that runs on port 8080.

usage: python api.py

(c) Javier Arias, Open Book Publishers, May 2019
Use of this software is governed by the terms of the MIT license

Dependencies:
  PyJWT==1.7.1
  psycopg2-binary==2.7.5
  python-dateutil==2.4.2
  web.py==0.40-dev1
"""

import os
import json
import sys
import web
import psycopg2
from aux import logger_instance, debug_mode, get_input
from errors import Error, InternalError, NotFound, NoMethod, NORESULT

# get logging interface
logger = logger_instance(__name__)
web.config.debug = debug_mode()

# override default http errors
web.webapi.nomethod = NoMethod
web.webapi.internalerror = InternalError
web.webapi.notfound = NotFound

# Define routes
urls = (
    "/events(/?)", "eventsctrl.EventsController",
    "/measures(/?)", "measuresctrl.MeasuresController"
)
# Set up application
app = web.application(urls, globals())
app.internalerror = InternalError

# Set up database connection and test it
db = web.database(dbn='postgres',
                  host=os.environ['POSTGRES_HOST'],
                  user=os.environ['POSTGRES_USER'],
                  pw=os.environ['POSTGRES_PASSWORD'],
                  db=os.environ['POSTGRES_DB'])
try:
    db._connect(db.keywords)
except psycopg2.DatabaseError as error:
    logger.error(error)
    sys.exit(1)


def api_response(fn):
    """Decorator to provided consistency in all responses"""
    def response(self, *args, **kw):
        logger.debug("Data: %s" % (get_input()))
        data = fn(self, *args, **kw)
        count = len(data)
        if not data:
            raise Error(NORESULT)
        return {'status': 'ok', 'code': 200, 'count': count, 'data': data}
    return response


def json_response(fn):
    """JSON decorator"""
    def response(self, *args, **kw):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        web.header('Access-Control-Allow-Origin',
                   '"'.join([os.environ['ALLOW_ORIGIN']]))
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers',
                   'Authorization, x-test-header, Origin, '
                   'X-Requested-With, Content-Type, Accept')
        return json.dumps(fn(self, *args, **kw), ensure_ascii=False)
    return response


if __name__ == "__main__":
    logger.info("Starting API...")
    app.run()
