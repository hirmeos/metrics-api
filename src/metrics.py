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
# Get secret key to check JWT
SECRET_KEY = ""
try:
    SECRET_KEY = os.environ['SECRET_KEY']
    if not SECRET_KEY:
        raise KeyError
except KeyError as error:
    logger.error(error)
    raise

# Define routes
urls = (
    "/metrics(/?)", "MetricsDB",
    "(.*)", "NotFound",
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


def get_token_from_header():
    bearer = web.ctx.env.get('HTTP_AUTHORIZATION', '')
    return bearer.replace("Bearer ", "") if bearer else ""


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


class RequestBroker(object):
    """Handles HTTP requests"""

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        """Get Events for a given object ID"""
        logger.debug("Request: '%s'; Query: %s" % (name, web.input()))

        uri = web.input().get('uri') or web.input().get('URI')
        try:
            assert uri
        except AssertionError:
            logger.debug("Invalid URI provided")
            raise NotFound()

        results = self.get_obj_events(uri)
        data = []
        for e in results:
            event = Event(e[0], e[1], e[2], e[3], e[4], e[5], e[6])
            data.append(event.__dict__)

        web.header('Access-Control-Allow-Origin', '*')

        return data

    @json_response
    @api_response
    @check_token
    def POST(self, name=None):
        """Create a new event"""
        data = json.loads(web.data())
        return save_new_entry(data)

    def PUT(self, name):
        raise NotAllowed()

    def DELETE(self, name):
        raise NotAllowed()

    @json_response
    def OPTIONS(self, name):
        web.header('Access-Control-Allow-Methods', 'OPTIONS, GET, HEAD')
        web.header('Access-Control-Allow-Headers', 'authorization')
        web.header('Access-Control-Allow-Origin', '*')

        return {'status': 'ok'}


class MetricsDB(RequestBroker):
    """PostgesDB handler."""

    def get_obj_events(self, key):
        result = Event.get_events(str(key))
        if result is not None:
            return result
        else:
            logger.debug("No data for URI: %s" % (key))
            raise NotFound()


if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = internal_error
    app.notfound = not_found
    app.run()
