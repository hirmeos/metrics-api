#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage metrics JSON API. Simple web.py based API to a
PostgreSQL database that runs on port 8080.

usage: python apis.py

(c) Javier Arias, Open Book Publishers, May 2019
Use of this software is governed by the terms of the MIT license

Dependencies:
  PyJWT==1.7.1
  psycopg2-binary==2.7.5
  python-dateutil==2.4.2
  web.py==0.39
"""

import re
import os
import web
import json
import jwt
import datetime
from aux import logger_instance, debug_mode
from errors import (Error, internal_error, not_found, NORESULT, UNAUTHORIZED,
                    FORBIDDEN, BADFILTERS, BADPARAMS)

# get logging interface
logger = logger_instance(__name__)
web.config.debug = debug_mode()
# You may disable JWT auth. when implementing the API in a local network
JWT_DISABLED = False
# Get secret key to check JWT
SECRET_KEY = os.getnenv('SECRET_KEY')
try:
    if 'JWT_DISABLED' in os.environ:
        JWT_DISABLED = os.environ['JWT_DISABLED'] in ('true', 'True')
    assert JWT_DISABLED or SECRET_KEY
except AssertionError as error:
    logger.error(error)
    raise

# Define routes
urls = (
    "/events(/?)", "eventsctrl.EventsController",
    "/measures(/?)", "measuresctrl.MeasuresController"
)

try:
    db = web.database(dbn='postgres',
                      host=os.environ['POSTGRES_HOST'],
                      user=os.environ['POSTGRES_USER'],
                      pw=os.environ['POSTGRES_PASSWORD'],
                      db=os.environ['POSTGRES_DB'])
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


def decode_token(intoken):
    try:
        return jwt.decode(intoken, SECRET_KEY)
    except jwt.exceptions.DecodeError:
        raise Error(FORBIDDEN)
    except jwt.ExpiredSignatureError:
        raise Error(UNAUTHORIZED, msg="Signature expired.")
    except jwt.InvalidTokenError:
        raise Error(UNAUTHORIZED, msg="Invalid token.")


def valid_user(fn):
    """Decorator to act as middleware, checking token"""
    def response(self, *args, **kw):
        if not is_user() or is_admin():
            raise Error(UNAUTHORIZED, msg="You lack write rights.")
        return fn(self, *args, **kw)
    return response


def admin_user(fn):
    """Decorator to act as middleware, checking token for admin rights"""
    def response(self, *args, **kw):
        if not is_admin():
            raise Error(UNAUTHORIZED, msg="You lack admin rights.")
        return fn(self, *args, **kw)
    return response


def check_token(fn):
    """Decorator to act as middleware, checking authentication token"""
    def response(self, *args, **kw):
        if decode_token(get_token_from_header()):
            return fn(self, *args, **kw)
    return response


def is_admin():
    return get_authority_from_token() == 'admin'


def is_user():
    return get_authority_from_token() == 'user'


def get_uploader_from_token():
    return decode_token(get_token_from_header())['sub']


def get_authority_from_token():
    return decode_token(get_token_from_header())['authority']


def build_params(filters):
    if not filters:
        return "", {}
    # split by ',' except those preceeded by a top level domain, which will
    # be a tag URI scheme (e.g. tag:openbookpublishers.com,2009)
    params    = re.split(r"(?<!\.[a-z]{3}),", filters)
    options   = {}
    uris      = []
    measures  = []
    countries = []
    uploaders = []
    clause  = ""
    for p in params:
        try:
            field, val = p.split(':', 1)
            if field == "work_uri":
                uris.append(val)
            elif field == "measure_uri":
                measures.append(val)
            elif field == "country_uri":
                countries.append(val)
            elif field == "uploader_uri":
                uploaders.append(val)
            else:
                raise Error(BADFILTERS)
        except BaseException:
            raise Error(BADFILTERS, msg="Unknown filter '%s'" % (p))

    process = {"work_uri": uris, "measure_uri": measures,
               "country_uri": countries, "uploader_uri": uploaders}
    for key, values in process.items():
        if len(values) > 0:
            try:
                andclause, ops = build_clause(key, values)
                options.update(ops)
                clause = clause + andclause
            except BaseException:
                raise Error(BADFILTERS)

    return clause, options


def build_clause(attribute, values):
    params = {}
    clause = " AND " + attribute + " IN ("
    no = 1
    for v in values:
        params[attribute + str(no)] = v
        if no > 1:
            clause += ","
        clause += "$" + attribute + str(no)
        no += 1
    return [clause + ")", params]


def build_date_clause(start_date, end_date):
    if not end_date:
        end_date = datetime.date.today().strftime("%Y-%m-%d")
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        msg = "start_date and end_date must be in YYYY-MM-DD format"
        raise Error(BADPARAMS, msg=msg)
    clause = " AND timestamp BETWEEN $start_date AND $end_date"
    params = {'start_date': start_date, 'end_date': end_date}
    return [clause, params]


if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = internal_error
    app.notfound = not_found
    app.run()
