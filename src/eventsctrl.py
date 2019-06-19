import web
import uuid
from aux import logger_instance, debug_mode
from api import (json, json_response, api_response, valid_user, build_params,
                 build_date_clause, get_uploader_from_token)
from errors import Error, NOTALLOWED, BADPARAMS, NORESULT
from models import (Event, results_to_events, results_to_measure_aggregation,
                    results_to_measure_country_aggregation,
                    results_to_country_measure_aggregation,
                    results_to_measure_year_aggregation,
                    results_to_year_measure_aggregation,
                    results_to_measure_month_aggregation,
                    results_to_month_measure_aggregation)
from dateutil import parser


logger = logger_instance(__name__)
web.config.debug = debug_mode()


class EventsController(object):
    """Handles work related actions"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Events with various filtering options"""
        logger.debug("Query: %s" % (web.input()))

        event_id = web.input().get('event_id')

        if event_id:
            results = Event.get_from_event_id(event_id)
            data = results_to_events(results)
        else:
            filters = web.input().get('filter')
            clause, params = build_params(filters)

            start_date = web.input().get('start_date')
            end_date = web.input().get('end_date')
            if start_date:
                dclause, dparams = build_date_clause(start_date, end_date)
                clause += dclause
                params.update(dparams)

            agg = web.input().get('aggregation') or ''
            if agg == '':
                results = Event.get_all(clause, params)
                data = results_to_events(results)
            elif agg == 'measure_uri':
                results = Event.aggregate_by_measure(clause, params)
                data = results_to_measure_aggregation(results)
            elif agg == 'measure_uri,country_uri':
                results = Event.aggregate_by_measure_country(clause, params)
                data = results_to_measure_country_aggregation(results)
            elif agg == 'country_uri,measure_uri':
                results = Event.aggregate_by_country_measure(clause, params)
                data = results_to_country_measure_aggregation(results)
            elif agg == 'measure_uri,year':
                results = Event.aggregate_by_measure_year(clause, params)
                data = results_to_measure_year_aggregation(results)
            elif agg == 'year,measure_uri':
                results = Event.aggregate_by_year_measure(clause, params)
                data = results_to_year_measure_aggregation(results)
            elif agg == 'measure_uri,month':
                results = Event.aggregate_by_measure_month(clause, params)
                data = results_to_measure_month_aggregation(results)
            elif agg == 'month,measure_uri':
                results = Event.aggregate_by_month_measure(clause, params)
                data = results_to_month_measure_aggregation(results)
            else:
                m = "Aggregation must be one of the following: 'measure_uri', "
                "'measure_uri,country_uri', 'country_uri,measure_uri', "
                "'measure_uri,year', 'year,measure_uri', 'measure_uri,month', "
                "'month,measure_uri'"
                raise Error(BADPARAMS, msg=m)

        if not data:
            raise Error(NORESULT)
        return data

    @json_response
    @api_response
    @valid_user
    def POST(self, name=None):
        """Create a new event"""
        data = json.loads(web.data())
        return save_event(data)

    @json_response
    @api_response
    @valid_user
    def PUT(self, name):
        """Update an event"""
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    @valid_user
    def DELETE(self, name):
        """Delete an event"""
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return


def save_event(data):
    """Store a new event."""
    try:
        work_uri = data.get('work_uri')
        measure_uri = data.get('measure_uri')
        timestamp = parser.parse(data.get('timestamp'))
        value = data.get('value')
        event_uri = data.get('event_uri') or None
        country_uri = data.get('country_uri') or None
        uploader_uri = get_uploader_from_token()
        if not all([work_uri, measure_uri, timestamp, value, uploader_uri]):
            raise AssertionError
    except BaseException:
        raise Error(BADPARAMS)

    event_id = str(uuid.uuid4())
    event = Event(event_id, work_uri, measure_uri, timestamp, value, event_uri,
                  country_uri, uploader_uri)
    event.save()
    return [event.__dict__]
