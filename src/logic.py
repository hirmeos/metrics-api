from dateutil import parser
import logging

from errors import NotFound
from models import Event


logger = logging.getLogger(__name__)


def save_new_entry(data):
    """Save new text entry from the altmetrics service."""

    uri = data.get('uri')
    measure = data.get('measure')
    value = data.get('value')
    country = data.get('country')
    uploader = data.get('uploader')
    timestamp = parser.parse(data.get('timestamp'))

    try:
        assert all([uri, measure, timestamp, value, uploader])
    except AssertionError as error:
        logger.debug(error)
        logger.debug("Invalid parameters provided: %s" % data)
        raise NotFound()

    event = Event(None, uri, measure, timestamp, value, country, uploader)
    event.save()

    return "Metrics submitted."
