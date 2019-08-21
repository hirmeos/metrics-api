#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import web


def debug_mode():
    return str(os.environ.get('API_DEBUG')).lower() in ('true', '1')


def test_mode():
    return os.environ.get('WEBPY_ENV') == 'test'


def logger_instance(name):
    level = logging.NOTSET if debug_mode() else logging.ERROR
    logging.basicConfig(level=level)
    return logging.getLogger(name)


def strtolist(data):
    if isinstance(data, str) or isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data


def is_get_request():
    return web.ctx.env.get('REQUEST_METHOD', '') == 'GET'


def get_input():
    return web.input() if is_get_request() else web.data().decode('utf-8')
