import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
from src.database.models import EventModel
from src.config import Config

MQTT_BROKER = "172.18.0.2"
MQTT_PORT = 1883
EVENTS_TOPIC = "gate/events"

class MqttEventService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()

    
    def publish_event(self, event_type, plate):
        poc_id = Config.POC_ID
        event_id = str(uuid.uuid4())
        event_model = EventModel()
        event_model.register_event(event_id, event_type, poc_id, plate)  # Guarda en BD local

        payload = json.dumps({"id": event_id, "pocId": poc_id, "type": event_type, "plate": plate})
        print(payload)
        self.client.publish(EVENTS_TOPIC, payload)

