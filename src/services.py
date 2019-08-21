from aux import logger_instance
from eventsctrl import save_event
from nameko.events import event_handler

logger = logger_instance(__name__)


class NewEventServiceReceiver():
    """Nameko receiver to listen for new text entries from Jura."""

    name = 'altmetrics_data_service'

    @event_handler('metrics_api_service', 'new_entry')
    def save_entry(self, data):
        try:
            save_event(data, from_nameko=True)
            logger.info("New altmetrics entry successfully saved.")
        except BaseException:
            msg = "[{work_uri}-{event_uri}] - FAILED TO SAVE ALTMETRICS EVENT."
            logger.error(msg.format(**data))
