#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import web
import jwt
from aux import logger_instance
from errors import Error, UNAUTHORIZED, FORBIDDEN, FATAL

logger = logger_instance(__name__)

# You may disable JWT auth. when implementing the API in a local network
JWT_DISABLED = os.getenv('JWT_DISABLED', 'false').lower() == 'true'
# Get secret key to check JWT
SECRET_KEY = os.getenv('SECRET_KEY')

if not JWT_DISABLED and not SECRET_KEY:
    logger.error("API authentication is not configured. "
                 "You must set JWT_DISABLED or SECRET_KEY")
    raise Error(FATAL)


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
        if not is_user() and not is_admin():
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
