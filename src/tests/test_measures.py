import json
from nose.tools import assert_equals, ok_
from .testapp import App


class TestMeasures():
    def __init__(self):
        self.app = App()

    def test_get_all_measures(self):
        res = self.app.get('/measures', status=200)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "ok")
        ok_(results["data"])

    def test_not_allowed_post(self):
        res = self.app.post('/measures', status=405)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 405)

    def test_not_allowed_put(self):
        res = self.app.put('/measures', status=405)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 405)

    def test_not_allowed_delete(self):
        res = self.app.delete('/measures', status=405)
        results = json.loads(res.body.decode('utf-8'))
        assert_equals(results["status"], "error")
        assert_equals(results["code"], 405)
