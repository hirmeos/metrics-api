#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage metrics JSON API. Simple web.py based API to a
PostgreSQL database that runs on port 8080.

usage: python metrics.py

(c) Javier Arias, Open Book Publishers, May 2019
Use of this software is governed by the terms of the MIT license

Dependencies:
  python-dateutil==2.4.2
  psycopg2==2.6.1
  web.py==0.38
"""

import os
import web
import json
import jwt
from aux import logger_instance, debug_mode
from errors import Error, internal_error, not_found, \
    NORESULT, BADFILTERS, UNAUTHORIZED, FORBIDDEN
from models import Event
from logic import save_new_entry

# get logging interface
logger = logger_instance(__name__)
web.config.debug = debug_mode()
# You may disable JWT auth. when implementing the API in a local network
JWT_DISABLED = False
# Get secret key to check JWT
SECRET_KEY = ""
try:
    if 'JWT_DISABLED' in os.environ:
        JWT_DISABLED = os.environ['JWT_DISABLED'] in ('true', 'True')
    if 'SECRET_KEY' in os.environ:
        SECRET_KEY = os.environ['SECRET_KEY']
    assert JWT_DISABLED or SECRET_KEY
except AssertionError as error:
    logger.error(error)
    raise

# Define routes
urls = (
    "/metrics(/?)", "metricsctrl.MetricsController"
)

try:
    db = web.database(dbn='postgres',
                      host=os.environ['POSTGRESDB_HOST'],
                      user=os.environ['POSTGRESDB_USER'],
                      pw=os.environ['POSTGRESDB_PASSWORD'],
                      db=os.environ['POSTGRESDB_DB'])
except Exception as error:
    logger.error(error)
    raise


def api_response(fn):
    """Decorator to provided consistency in all responses"""
    def response(self, *args, **kw):
        data  = fn(self, *args, **kw)
        count = len(data)
        if count > 0:
            return {'status': 'ok', 'code': 200, 'count': count, 'data': data}
        else:
            raise Error(NORESULT)
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


def check_token(fn):
    """Decorator to act as middleware, checking authentication token"""
    def response(self, *args, **kw):
        intoken = get_token_from_header()
        try:
            jwt.decode(intoken, SECRET_KEY)
        except jwt.exceptions.DecodeError:
            raise Error(FORBIDDEN)
        except jwt.ExpiredSignatureError:
            raise Error(UNAUTHORIZED, msg="Signature expired.")
        except jwt.InvalidTokenError:
            raise Error(UNAUTHORIZED, msg="Invalid token.")
        return fn(self, *args, **kw)
    return response


def get_token_from_header():
    bearer = web.ctx.env.get('HTTP_AUTHORIZATION', '')
    return bearer.replace("Bearer ", "") if bearer else ""


if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = internal_error
    app.notfound = not_found
    app.run()
