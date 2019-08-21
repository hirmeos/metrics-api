from api import db
import psycopg2
from errors import Error, FATAL
from aux import logger_instance

logger = logger_instance(__name__)

_GET_ALL = "SELECT * FROM event WHERE 1=1 {} ORDER BY timestamp;"
_MEASURE = """
    SELECT
      measure_uri,
      namespace,
      source,
      type,
      version,
      SUM(value) as value
    FROM event INNER JOIN measure USING(measure_uri)
    WHERE 1=1 {}
    GROUP BY measure_uri, namespace, source, type, version
    ORDER BY measure_uri;"""
_MEASURE_COUNTRY = """
    SELECT
      measure_uri,
      namespace,
      source,
      type,
      version,
      country_uri,
      country_code,
      country_name,
      continent_code,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
      LEFT JOIN country USING(country_uri)
    WHERE 1=1 {}
    GROUP BY measure_uri, namespace, source, type, version,
      country_uri, country_code, country_name, continent_code
    ORDER BY measure_uri, country_uri;"""
_COUNTRY_MEASURE = """
    SELECT
      country_uri,
      country_code,
      country_name,
      continent_code,
      measure_uri,
      namespace,
      source,
      type,
      version,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
      LEFT JOIN country USING(country_uri)
    WHERE 1=1 {}
    GROUP BY country_uri, country_code, country_name,
      continent_code, measure_uri, namespace, source,
      type, version
    ORDER BY country_uri, measure_uri;"""
_MEASURE_YEAR = """
    SELECT
      measure_uri,
      namespace,
      source,
      type,
      version,
      to_char(timestamp, 'YYYY') as year,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
    WHERE 1=1 {}
    GROUP BY measure_uri, namespace, source, type, version, year
    ORDER BY measure_uri, year;"""
_YEAR_MEASURE = """
    SELECT
      to_char(timestamp, 'YYYY') as year,
      measure_uri,
      namespace,
      source,
      type,
      version,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
    WHERE 1=1 {}
    GROUP BY year, measure_uri, namespace, source, type, version
    ORDER BY year, measure_uri;"""
_MEASURE_MONTH = """
    SELECT
      measure_uri,
      namespace,
      source,
      type,
      version,
      to_char(timestamp, 'MM') as month,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
    WHERE 1=1 {}
    GROUP BY measure_uri, namespace, source, type, version,
      month
    ORDER BY measure_uri, month;"""
_MONTH_MEASURE = """
    SELECT
      to_char(timestamp, 'MM') as month,
      measure_uri,
      namespace,
      source,
      type,
      version,
      SUM(value) as value
    FROM event
      INNER JOIN measure USING(measure_uri)
    WHERE 1=1 {}
    GROUP BY month, measure_uri, namespace, source, type,
      version
    ORDER BY month, measure_uri;"""
AGGREGATION_QUERIES = {
    '': _GET_ALL,
    'measure_uri': _MEASURE,
    'measure_uri,country_uri': _MEASURE_COUNTRY,
    'country_uri,measure_uri': _COUNTRY_MEASURE,
    'measure_uri,year': _MEASURE_YEAR,
    'year,measure_uri': _YEAR_MEASURE,
    'measure_uri,month': _MEASURE_MONTH,
    'month,measure_uri': _MONTH_MEASURE
}


def dbcheck(function):
    """Decorator to catch database errors"""
    def response(*args, **kw):
        try:
            return function(*args, **kw)
        except psycopg2.DatabaseError as error:
            logger.error(error)
            raise Error(FATAL)
    return response


@dbcheck
def do_query(query, params={}):
    return db.query(query, params)
