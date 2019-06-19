import web
from aux import logger_instance, debug_mode
from api import json_response, api_response, valid_user
from errors import Error, NOTALLOWED, NORESULT
from models import Measure, results_to_measures

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class MeasuresController(object):
    """Handles work related actions"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Measures with descriptions"""
        results = Measure.get_all()
        data = results_to_measures(results, True)

        if not data:
            raise Error(NORESULT)
        return data

    @json_response
    @api_response
    @valid_user
    def POST(self, name):
        """Create a new measure"""
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    @valid_user
    def PUT(self, name):
        """Update an measure"""
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    @valid_user
    def DELETE(self, name):
        """Delete an measure"""
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return
