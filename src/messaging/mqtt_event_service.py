import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
from src.database.models import EventModel
from src.config import Config
import logging

MQTT_BROKER = Config.MQTT_SERVER_HOST
MQTT_PORT = 1883
EVENTS_TOPIC = "local-events/" + Config.ENTITY_ID + "/create"
PENDING_EVENTS_TOPIC = "pending-events/"+ Config.ENTITY_ID + "/sync"

class MqttEventService:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = mqtt.Client()
        self.event_model = EventModel()

        # Configurar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

        # Conectar al broker
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker")
        else:
            self.logger.error(f"Error connection to MQTT broker, error code: {rc}")

    def on_publish(self, client, userdata, mid):
        self.logger.info(f"Message published successfully with ID: {mid}")

    def on_disconnect(self, client, userdata, rc):
        self.logger.warning("Desconnected from broker")

    def publish_event(self, event_type, plate):
        poc_id = Config.POC_ID
        event_id = str(uuid.uuid4())
        self.event_model.register_event(event_id, event_type, poc_id, plate)

        payload = json.dumps({"id": event_id, "pocId": poc_id, "type": event_type, "plate": plate})

        #result, mid = self.client.publish(EVENTS_TOPIC, payload, qos=2)

        #if result == mqtt.MQTT_ERR_SUCCESS:
        #    self.event_model.mark_event_as_synced(event_id)
        #else:
        #    self.logger.error(f"Error sending message to MQTT broker: {result}")
            
    def publish_pending_events(self, event_buffer):
        """
        Send pending events batch to server and mark them as synchronized in the database.
        """
        if not event_buffer:
            return

        try:
            batch_id = str(datetime.now())
            
            payload = json.dumps({"batchId": batch_id, "events": event_buffer})
            
            result, mid = self.client.publish(PENDING_EVENTS_TOPIC, payload, qos=1)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Batch sent successfully: {len(event_buffer)} events")
                
                event_ids = [event["id"] for event in event_buffer]
                self.logger.info("logg tsss")
                self.event_model.mark_batch_as_sync(event_ids) 
            
            else:
                self.logger.warning(f"Error sending pending events batch: {result}")
        except Exception as ex:
            self.logger.error(f"Exception sending pending events batch: {ex}")