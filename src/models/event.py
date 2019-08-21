from .queries import AGGREGATION_QUERIES, do_query


class Event():
    def __init__(self, event_id, work_uri, measure_uri, timestamp, value,
                 event_uri=None, country_uri=None, uploader_uri=''):
        self.event_id = event_id
        self.work_uri = work_uri
        self.measure_uri = measure_uri
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value = int(value)
        self.event_uri = event_uri
        self.country_uri = country_uri
        self.uploader_uri = uploader_uri

    def save(self):
        q = '''INSERT INTO event (event_id, work_uri, measure_uri,
                  timestamp, value, event_uri, country_uri, uploader_uri)
                VALUES ($event_id, $work_uri, $measure_uri, $timestamp,
                  $value, $event_uri, $country_uri, $uploader_uri)
                ON CONFLICT DO NOTHING;'''
        do_query(q, self.__dict__)

    @staticmethod
    def get_from_event_id(event_id):
        params = dict(event_id=event_id)
        clause = "AND event_id = $event_id"
        return Event.get_all(clause, params)

    @staticmethod
    def get_all(clause, params):
        return Event.get_for_aggregation('', clause, params)

    @staticmethod
    def get_for_aggregation(criterion, clause, params):
        return do_query(AGGREGATION_QUERIES[criterion].format(clause), params)
