import psycopg2
from api import db
from aux import logger_instance
from errors import Error, FATAL

logger = logger_instance(__name__)


class Event(object):
    def __init__(self, event_id, work_uri, measure_uri, timestamp, value,
                 event_uri=None, country_uri=None, uploader_uri=''):
        self.event_id = event_id
        self.work_uri = work_uri
        self.measure_uri = measure_uri
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value = int(value)
        self.event_uri = event_uri
        self.country_uri = country_uri
        self.uploader_uri = uploader_uri

    def save(self):
        try:
            q = '''INSERT INTO event (event_id, work_uri, measure_uri,
                      timestamp, value, event_uri, country_uri, uploader_uri)
                    VALUES ($event_id, $work_uri, $measure_uri, $timestamp,
                      $value, $event_uri, $country_uri, $uploader_uri)
                    ON CONFLICT DO NOTHING;'''
            vals = dict(event_id=self.event_id, work_uri=self.work_uri,
                        measure_uri=self.measure_uri, timestamp=self.timestamp,
                        value=self.value, event_uri=self.event_uri,
                        country_uri=self.country_uri, uploader=self.uploader)
            db.query(q, vals)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_event_id(event_id):
        params = dict(event_id=event_id)
        clause = "AND event_id = $event_id"
        return Event.get_all(clause, params)

    @staticmethod
    def get_all(clause, params):
        try:
            q = '''SELECT * FROM event WHERE 1=1 ''' + clause + '''
                   ORDER BY timestamp;'''
            return db.query(q, params)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version
                   ORDER BY measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_country(clause, params):
        try:
            q = '''SELECT
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
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version,
                      country_uri, country_code, country_name, continent_code
                   ORDER BY measure_uri, country_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_country_measure(clause, params):
        try:
            q = '''SELECT
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
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY country_uri, country_code, country_name,
                      continent_code, measure_uri, namespace, source,
                      type, version
                   ORDER BY country_uri, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_year(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     to_char(timestamp, 'YYYY') as year,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version, year
                   ORDER BY measure_uri, year;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_year_measure(clause, params):
        try:
            q = '''SELECT
                     to_char(timestamp, 'YYYY') as year,
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY year, measure_uri, namespace, source, type, version
                   ORDER BY year, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_month(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     to_char(timestamp, 'MM') as month,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version,
                     month
                   ORDER BY measure_uri, month;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_month_measure(clause, params):
        try:
            q = '''SELECT
                     to_char(timestamp, 'MM') as month,
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY month, measure_uri, namespace, source, type,
                     version
                   ORDER BY month, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)


class Measure(object):
    def __init__(self, measure_uri, namespace, source, mtype, version):
        self.measure_uri = measure_uri
        self.namespace = namespace
        self.source = source
        self.type = mtype
        self.version = version

    def load_description(self):
        description = self.get_description()
        self.description = description.list() if description else []

    def get_description(self):
        options = dict(uri=self.measure_uri)
        q = '''SELECT locale_code, locale_name, description
               FROM measure_description INNER JOIN locale USING(locale_code)
               WHERE measure_uri = $uri
               ORDER BY locale_code;'''
        return db.query(q, options)

    @staticmethod
    def get_all():
        try:
            return db.select('measure')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)


class Country(object):
    def __init__(self, country_uri, country_code, country_name, continent):
        self.country_uri = country_uri
        self.country_code = country_code
        self.country_name = country_name
        self.continent_code = continent


def result_to_event(r):
    return Event(r["event_id"], r["work_uri"], r["measure_uri"],
                 r["timestamp"], r["value"], r["event_uri"],
                 r["country_uri"], r["uploader_uri"])


def result_to_country(r):
    return Country(r["country_uri"], r["country_code"], r["country_name"],
                   r["continent_code"])


def result_to_measure(r, description=False):
    measure = Measure(r["measure_uri"], r["namespace"], r["source"], r["type"],
                      r["version"])
    if description:
        measure.load_description()
    return measure


def results_to_events(results):
    return [(result_to_event(e).__dict__) for e in results]


def results_to_countries(results):
    return [(result_to_country(e).__dict__) for e in results]


def results_to_measures(results, description=False):
    return [(result_to_measure(e, description).__dict__) for e in results]


def results_to_measure_aggregation(results):
    data = []
    for r in results:
        measure = Measure(r["measure_uri"], r["namespace"], r["source"],
                          r["type"], r["version"])
        measure.value = r["value"]
        data.append(measure.__dict__)
    return data


def results_to_measure_country_aggregation(results):
    data = []
    countries = []  # temporary list of countries
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = countries
            data.append(measure.__dict__)
            countries = []
            cur = r
        country = result_to_country(r)
        country.value = r["value"]
        countries.append(country.__dict__)
        if i == last:
            measure = result_to_measure(cur)
            measure.data = countries
            data.append(measure.__dict__)
    return data


def results_to_country_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["country_uri"] != cur["country_uri"]:
            country = result_to_country(cur)
            country.data = measures
            data.append(country.__dict__)
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
        if i == last:
            country = result_to_country(cur)
            country.data = measures
            data.append(country.__dict__)
    return data


def results_to_measure_year_aggregation(results):
    data = []
    years = []  # temporary list of years
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = years
            data.append(measure.__dict__)
            years = []
            cur = r
        years.append(dict(year=r["year"], value=r["value"]))
        if i == last:
            measure = result_to_measure(cur)
            measure.data = years
            data.append(measure.__dict__)
    return data


def results_to_year_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["year"] != cur["year"]:
            data.append(dict(year=cur["year"], data=measures))
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
        if i == last:
            data.append(dict(year=cur["year"], data=measures))
    return data


def results_to_measure_month_aggregation(results):
    data = []
    months = []  # temporary list of months
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = months
            data.append(measure.__dict__)
            months = []
            cur = r
        months.append(dict(month=r["month"], value=r["value"]))
        if i == last:
            measure = result_to_measure(cur)
            measure.data = months
            data.append(measure.__dict__)
    return data


def results_to_month_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures
    last = len(results) - 1

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["month"] != cur["month"]:
            data.append(dict(month=cur["month"], data=measures))
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
        if i == last:
            data.append(dict(month=cur["month"], data=measures))
    return data
