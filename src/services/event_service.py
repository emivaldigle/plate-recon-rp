from src.config import Config
from src.database.models import EventModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono
from src.messaging.mqtt_event_service import MqttEventService
from datetime import datetime

class EventService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_db = EventModel()
        self.api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        self.mqtt_event = MqttEventService()
        self.event_buffer = []
        
    def build_api_event(self, event):
        return {
            "id": event[0],
            "pocId": event[1],
            "plate": event[2],
            "type": event[3],
            "createdAt": event[4]
        }
        
    def add_to_event_buffer(self, event):
        """
        Add provided event to buffer prior to send batch
        """    
        api_event = self.build_api_event(event)
        self.event_buffer.append(api_event)
        if len(self.event_buffer) >= 50:
            self.mqtt_event.publish_pending_events(self.event_buffer)
            
    def sync_pending_events(self):
        try:
            self.logger.info("Starting pending events syncronization")
            pending_events = self.event_db.find_pending_events()
            if pending_events is not None:
                for pending_event in pending_events:
                    self.add_to_event_buffer(pending_event)
                if self.event_buffer:
                    self.mqtt_event.publish_pending_events(self.event_buffer)
                    self.event_buffer.clear()
            else:
                self.logger.debug("Everything is up to date")
        except Exception as ex:
            self.logger.error(f"Unable to syncronize pending events {ex}")    

    def find_last_registered_event_type(self, plate):
        try:
            self.logger.info(f"Finding last event by license plate... {plate}")
            event = self.event_db.find_last_event_by_plate(plate)
            if event is None:
                self.logger.info(f"Event with license plate {plate} not found locally")
                entityId = Config.ENTITY_ID
                try:
                    remote_event = self.api_client.get(f"/events/entity/{entityId}/plate/{plate}")
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