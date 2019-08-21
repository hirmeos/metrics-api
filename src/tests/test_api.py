import json
from nose.tools import assert_equals
from .testapp import App

TEST_EVENT = {
    "work_uri": "info:doi:10.11647/obp.0020",
    "measure_uri": "https://metrics.operas-eu.org/world-reader/users/v1",
    "timestamp": "2019-01-01T01:00:00",
    "country_uri": "urn:iso:std:3166:-2:ES",
    "value": 512
}


class TestApi():
    def __init__(self):
        self.app = App()

    def test_index(self):
        res = self.app.get('/', status=404)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 404)

    def test_broken_api(self):
        res = self.app.get('/non-existent-api-call', status=404)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 404)
