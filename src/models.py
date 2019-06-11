import os
import uuid
import psycopg2
from api import db
from uri import URI
from aux import logger_instance
from errors import Error, FATAL

logger = logger_instance(__name__)

class Event(object):
    def __init__(self, event_id, uri, measure, timestamp, value, country, uploader):
        self.event_id  = str(event_id) if event_id else str(uuid.uuid4())
        self.URI       = str(uri)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country) if country else None
        self.uploader  = str(uploader)

    def save(self):
        try:
            connection = database_handle()
            c = connection.cursor()
            statement = (
                "INSERT INTO event (event_id, uri, measure_id,"
                "timestamp, country_id, value, uploader_id) VALUES "
                "('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    self.event_id, self.URI, self.measure, self.timestamp,
                    self.country, self.value, self.uploader
                )
            )
            c.execute(statement)
            success = connection.commit()
            return success
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()

    @staticmethod
    def get_events(key):
        try:
            c = database_handle().cursor()
            c.execute("SELECT * FROM event WHERE uri = %s;", (key,))
            result = c.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()
