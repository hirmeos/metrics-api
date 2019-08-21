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

    def test_get_all_events_from_fake_uri(self):
        uri = "info:doi:10.11647/obp.FAKE"
        params = {"filter": "work_uri:{}".format(uri)}
        res = self.app.get('/events', params, status=404)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 404)
        assert_equals(results["status"], "error")
        assert_equals(results["message"],
                      "No records have matched your search criteria.")

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

    def test_get_from_uri_aggregate_broken(self):
        uri = "info:doi:10.11647/obp.0001"
        params = {"filter": "work_uri:{}".format(uri), "aggregation": "fake"}
        res = self.app.get('/events', params, status=400)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 400)
        assert_equals(results["status"], "error")
        assert_equals(results["message"], "Invalid parameters provided.")

    def test_get_from_uri_aggregate_measure(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "measure_uri"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 4)
        expected = {
            "Google Books": 3,
            "OAPEN": 3,
            "Open Book Publishers HTML Reader": 3,
            "World Reader": 6
        }
        for value in results["data"]:
            assert_equals(value["value"], expected[value["source"]])

    def test_get_from_uri_aggregate_measure_country(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "measure_uri,country_uri"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 4)
        expected = {
            "Google Books": 1,
            "OAPEN": 2,
            "Open Book Publishers HTML Reader": 3,
            "World Reader": 2
        }
        for value in results["data"]:
            assert_equals(len(value["data"]), expected[value["source"]])

    def test_get_from_uri_aggregate_country_measure(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "country_uri,measure_uri"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 7)
        expected = {
            "Australia": 1,
            "Cuba": 1,
            "United Kingdom": 1,
            "New Zealand": 1,
            "Puerto Rico": 1,
            "United States of America": 1,
            None: 2
        }
        for value in results["data"]:
            assert_equals(len(value["data"]), expected[value["country_name"]])

    def test_get_from_uri_aggregate_measure_year(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "measure_uri,year"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 4)
        expected = {
            "Google Books": {"2018": 1, "2019": 2},
            "OAPEN": {"2018": 1, "2019": 2},
            "Open Book Publishers HTML Reader": {"2018": 1, "2019": 2},
            "World Reader": {"2018": 2, "2019": 4}
        }
        for measure in results["data"]:
            assert_equals(len(measure["data"]), 2)
            for value in measure["data"]:
                assert_equals(value["value"],
                              expected[measure["source"]][value["year"]])

    def test_get_from_uri_aggregate_year_measure(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "year,measure_uri"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 2)
        expected = {
            "2018": {
                "Google Books": 1,
                "OAPEN": 1,
                "Open Book Publishers HTML Reader": 1,
                "World Reader": 2
            },
            "2019": {
                "Google Books": 2,
                "OAPEN": 2,
                "Open Book Publishers HTML Reader": 2,
                "World Reader": 4
            }
        }
        for year in results["data"]:
            assert_equals(len(year["data"]), 4)
            for value in year["data"]:
                assert_equals(value["value"],
                              expected[year["year"]][value["source"]])

    def test_get_from_uri_aggregate_measure_month(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "measure_uri,month",
                  "start_date": "2019-01-01"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 4)
        expected = {
            "Google Books": {"01": 1, "02": 1},
            "OAPEN": {"01": 1, "02": 1},
            "Open Book Publishers HTML Reader": {"01": 1, "02": 1},
            "World Reader": {"01": 2, "02": 2}
        }
        for measure in results["data"]:
            assert_equals(len(measure["data"]), 2)
            for value in measure["data"]:
                assert_equals(value["value"],
                              expected[measure["source"]][value["month"]])

    def test_get_from_uri_aggregate_month_measure(self):
        uri = "info:doi:10.11647/obp.0002"
        params = {"filter": "work_uri:{}".format(uri),
                  "aggregation": "month,measure_uri",
                  "start_date": "2018-12-01",
                  "end_date": "2018-12-31"}
        res = self.app.get('/events', params, status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["code"], 200)
        assert_equals(results["status"], "ok")
        assert_equals(results["count"], 1)
        expected = {
            "12": {
                "Google Books": 1,
                "OAPEN": 1,
                "Open Book Publishers HTML Reader": 1,
                "World Reader": 2
            }
        }
        for month in results["data"]:
            assert_equals(len(month["data"]), 4)
            for value in month["data"]:
                assert_equals(value["value"],
                              expected[month["month"]][value["source"]])

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
