#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime
from aux import logger_instance
from errors import Error, BADFILTERS, BADPARAMS

logger = logger_instance(__name__)


def build_params(filters):
    if not filters:
        return "", {}
    options = {}
    uris = []
    measures = []
    countries = []
    uploaders = []
    clause = ""
    # split by ',' except those preceeded by a top level domain, which will
    # be a tag URI scheme (e.g. tag:openbookpublishers.com,2009)
    for p in re.split(r"(?<!\.[a-z]{3}),", filters):
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
    for key, values in list(process.items()):
        if values:
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
