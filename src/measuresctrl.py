import web

from api import json_response, api_response
from aux import logger_instance, debug_mode
from cache import set_cache_value, get_cache_value
from models.measure import Measure
from models.operations import results_to_measures


logger = logger_instance(__name__)
web.config.debug = debug_mode()


class MeasuresController:
    """Handles work related actions"""

    @json_response
    @api_response
    def GET(self, name):
        """Get Measures with descriptions"""
        redis_key = 'all-measures-with-descriptions'
        measures = get_cache_value(redis_key)

        if measures is None:
            measures = results_to_measures(Measure.get_all(), description=True)
            set_cache_value(redis_key, measures)

        return measures

    @json_response
    def OPTIONS(self, name):
        return
