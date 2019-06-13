import uuid
import psycopg2
from api import db
from aux import logger_instance
from errors import Error, FATAL

logger = logger_instance(__name__)


class Event(object):
    def __init__(self, event_id, uri, measure, timestamp, value, country,
                 uploader):
        self.event_id  = str(event_id) if event_id else str(uuid.uuid4())
        self.URI       = str(uri)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country) if country else None
        self.uploader  = str(uploader)

    def save(self):
        try:
            q = '''INSERT INTO event (event_id, uri, measure_id, timestamp,
                    country_id, value, uploader_id) VALUES ($event_id, $uri,
                    $measure_id, $timestamp, $country, $value, $uploader)
                    ON CONFLICT DO NOTHING'''
            db.query(q, dict(event_id=self.event_id, uri=self.URI,
                             measure=self.measure, timestamp=self.timestamp,
                             country=self.country, value=self.value,
                             uploader=self.uploader))
        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_events(key):
        options = dict(uri=key)
        return db.select('event', options, where="uri = $uri")
