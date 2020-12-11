from dateutil import parser
import json
import uuid

import web

from models.event import Event
from models.aggregation import Aggregation
from models.operations import results_to_events

from api import api_response, json_response
from auth import get_uploader_from_token, valid_user
from aux import debug_mode, logger_instance
from cache import redis_client
from errors import BADPARAMS, Error
from validation import build_date_clause, build_params


logger = logger_instance(__name__)
web.config.debug = debug_mode()


class EventsController:
    """Handles work related actions"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Events with various filtering options"""
        event_id = web.input().get('event_id')

        if event_id:
            value = redis_client.get_from_json(event_id)

            if value:
                data = json.loads(value)
            else:
                results = Event.get_from_event_id(event_id)
                data = results_to_events(results)
                redis_client.set_to_json(event_id, data)

        else:
            filters = web.input().get('filter')
            clause, params = build_params(filters)

            start_date = web.input().get('start_date')
            end_date = web.input().get('end_date')
            if start_date:
                dclause, dparams = build_date_clause(start_date, end_date)
                clause += dclause
                params.update(dparams)

            criterion = web.input().get('aggregation', '')

            query_args = [criterion, clause, params]
            redis_key = json.dumps(query_args)
            value = redis_client.get_from_json(redis_key)

            if value:
                data = json.loads(value)
            else:
                if not Aggregation.is_allowed(criterion):
                    raise Error(
                        BADPARAMS,
                        msg=f'Aggregation must be one of the following:'
                            f' {Aggregation.list_allowed()}.'
                    )

                aggregation = Aggregation(criterion)
                aggregation.data = Event.get_for_aggregation(*query_args)
                data = aggregation.aggregate()
                redis_client.set_to_json(redis_key, data)

        return data

    @json_response
    @api_response
    @valid_user
    def POST(self, name=None):
        """Create a new event"""
        data = json.loads(web.data().decode('utf-8'))
        return save_event(data)

    @json_response
    def OPTIONS(self, name):
        return


def save_event(data, from_nameko=False):
    """Store a new event. Ignore token if the event comes from Nameko."""
    try:
        work_uri = data.get('work_uri').lower()
        measure_uri = data.get('measure_uri')
        timestamp = parser.parse(data.get('timestamp'))
        value = data.get('value')
        event_uri = data.get('event_uri') or None
        country_uri = data.get('country_uri') or None

        if from_nameko:
            uploader_uri = data.get('uploader_uri')
        else:
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
