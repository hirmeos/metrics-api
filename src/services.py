from aux import logger_instance
from logic import save_new_entry
from nameko.events import event_handler

logger = logger_instance(__name__)


class NewEventServiceReceiver(object):
    """Nameko receiver to listen for new text entries from Jura."""

    name = 'altmetrics_data_service'

    @event_handler('metrics_api_service', 'new_entry')
    def save_entry(self, data):
        save_new_entry(data)
        logger.info("New altmetrics entry successfully saved.")
