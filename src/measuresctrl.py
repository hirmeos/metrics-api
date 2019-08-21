import web
from aux import logger_instance, debug_mode
from api import json_response, api_response
from models.measure import Measure
from models.operations import results_to_measures

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class MeasuresController():
    """Handles work related actions"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Measures with descriptions"""
        results = Measure.get_all()
        return results_to_measures(results, True)

    @json_response
    def OPTIONS(self, name):
        return
