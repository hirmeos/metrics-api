from api import db
from .queries import do_query, dbcheck


class Measure():
    def __init__(self, measure_uri, namespace, source, mtype, version):
        self.measure_uri = measure_uri
        self.namespace = namespace
        self.source = source
        self.type = mtype
        self.version = version

    def load_description(self):
        description = self.get_description()
        self.description = description.list() if description else []

    def get_description(self):
        options = dict(uri=self.measure_uri)
        q = '''SELECT locale_code, locale_name, description
               FROM measure_description INNER JOIN locale USING(locale_code)
               WHERE measure_uri = $uri
               ORDER BY locale_code;'''
        return do_query(q, options)

    @staticmethod
    @dbcheck
    def get_all():
        return db.select('measure')
