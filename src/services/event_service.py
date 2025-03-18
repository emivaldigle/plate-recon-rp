from src.config import Config
from src.database.models import EventModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class EventService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def find_last_registered_event_type(self, plate):
        event_db = EventModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        try:
            self.logger.info(f"Finding last event by license plate... {plate}")
            event = event_db.find_last_event_by_plate(plate)
            if event is None:
                self.logger.info(f"Event with license plate {plate} not found locally")
                entityId = Config.ENTITY_ID
                try:
                    remote_event = api_client.get(f"/events/entity/{entityId}/plate/{plate}")
                    if remote_event is not None:
                        return remote_event.get("type")
                except Exception as ex:
                    self.logger.warning("Unable to obtain event remotely")
                    return None
            else:
                return event[3]    
        except Exception as ex:
            self.logger.error(f"Unable to obtain event {ex}")
            return None