import json
from nose.tools import assert_equals, ok_
from .testapp import App, AuthApp

TEST_EVENT = {
    "work_uri": "info:doi:10.11647/obp.0020",
    "measure_uri": "https://metrics.operas-eu.org/world-reader/users/v1",
    "timestamp": "2019-01-01T01:00:00",
    "country_uri": "urn:iso:std:3166:-2:ES",
    "value": 512
}


class TestEvents():
    def __init__(self):
        self.app = App()
        self.authapp = AuthApp()

    def test_get_all_events(self):
        res = self.app.get('/events', status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 30)
        ok_(results["data"])

    def test_get_event_from_id(self):
        params = {"event_id": "6b77d272-6a9b-418e-970f-e261855b3fce"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 1)
        assert_equals(results["data"][0]["value"], 1)
        assert_equals(results["data"][0]["work_uri"],
                      "info:doi:10.11647/obp.0001")
        assert_equals(results["data"][0]["measure_uri"],
                      "https://metrics.operas-eu.org/world-reader/users/v1")
        assert_equals(results["data"][0]["country_uri"],
                      "urn:iso:std:3166:-2:ES")

    def test_get_all_events_from_uri(self):
        uri = "info:doi:10.11647/obp.0001"
        params = {"filter": "work_uri:{}".format(uri)}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 15)
        assert_equals(results["data"][0]["work_uri"], uri)
        ok_(results["data"])

    def test_get_all_events_from_uri_and_start_date(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "start_date": "2019-01-01"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 10)
        assert_equals(results["data"][0]["work_uri"], uri)
        ok_(results["data"])

    def test_get_all_events_from_uri_and_dates(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "start_date": "2019-01-01", "end_date": "2019-01-30"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 5)
        assert_equals(results["data"][0]["work_uri"], uri)
        assert_equals(results["data"][0]["timestamp"],
                      "2019-01-01T00:00:00+0000")
        ok_(results["data"])

    def test_post_unauth(self):
        payload = {}
        res = self.app.post('/events', payload, status=403)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 403)
        assert_equals(results["message"],
                      "You do not have permissions to access this resource.")

    def test_post_auth_empty(self):
        headers = self.authapp.auth_headers
        res = self.authapp.post('/events', params='{}', headers=headers,
                                status=400)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 400)
        assert_equals(results["message"], "Invalid parameters provided.")

    def test_post_auth_trivial(self):
        headers = self.authapp.auth_headers
        res = self.app.post('/events', params=json.dumps(TEST_EVENT),
                            headers=headers, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "ok")
        assert_equals(results["code"], 200)

    def test_post_auth_readback(self):
        headers = self.authapp.auth_headers
        res = self.app.post('/events', params=json.dumps(TEST_EVENT),
                            headers=headers, status=200)

        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "ok")
        for key, value in TEST_EVENT.items():
            assert_equals(results["data"][0][key], TEST_EVENT[key])
        assert_equals(results["data"][0]["uploader_uri"],
                      "acct:javi@openbookpublishers.com")

    def test_not_allowed_put(self):
        res = self.app.put('/events', status=405)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 405)

    def test_not_allowed_delete(self):
        res = self.app.delete('/events', status=405)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 405)
