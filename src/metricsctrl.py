import re
import web
from aux import logger_instance, debug_mode, strtolist
from api import json, json_response, api_response, valid_user, build_parms
from errors import Error, NOTALLOWED, BADPARAMS, BADFILTERS, NORESULT
from models import Work, WorkType, Identifier, UriScheme, results_to_works

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class MetricsController(object):
    """Handles work related actions"""

    @json_response
    @api_response
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
        return data

    @json_response
    @api_response
    @valid_user
    def POST(self, name=None):
        """Create a new event"""
        data = json.loads(web.data())
        return save_new_entry(data)

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