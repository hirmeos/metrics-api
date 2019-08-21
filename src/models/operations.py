from aux import logger_instance
from .event import Event
from .country import Country
from .measure import Measure
from .datepart import Datepart

logger = logger_instance(__name__)


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


def result_to_date_part(year=None, month=None):
    return Datepart(year=year, month=month)


def result_to_year(r):
    return result_to_date_part(year=r["year"])


def result_to_month(r):
    return result_to_date_part(month=r["month"])


def results_to_events(results):
    return [(result_to_event(e).__dict__) for e in results]


def results_to_countries(results):
    return [(result_to_country(e).__dict__) for e in results]


def results_to_measures(results, description=False):
    return [(result_to_measure(e, description).__dict__) for e in results]
