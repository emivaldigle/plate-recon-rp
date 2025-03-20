import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
from src.database.models import ParkingModel
from src.config import Config
import logging

MQTT_BROKER = Config.MQTT_SERVER_HOST
MQTT_PORT = 1883
EVENTS_TOPIC = "local-parking/" + Config.ENTITY_ID + "/update"
SUBSCRIBE_TOPIC = "parking/" + Config.ENTITY_ID + "/update" 

class MqttParkingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = mqtt.Client()
        self.parking_db = ParkingModel()
        # Configurar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Conectar al broker
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()
    
    def subscribe_on_topic(self):
        self.client.subscribe(SUBSCRIBE_TOPIC, qos=2)  # Suscribirse al tópico

    def on_message(self, client, userdata, msg):
        """
        Callback that process updates made in parking remotely
        """
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            self.logger.info(f"Received message: {payload}")

            # Extraer datos del mensaje
            identifier = payload.get("identifier")
            remote_last_updated_at = payload.get("lastUpdatedAt")
            
            if not identifier or not remote_last_updated_at:
                self.logger.error("Invalid message received: missing required fields")
                return

            # Obtener datos locales
            local_parking = self.parking_db.find_parking_by_identifier(identifier)
            if not local_parking:
                self.logger.error(f"No local parking found for identifier: {identifier}")
                return

            local_last_updated_at = local_parking[8]

            # Convertir fechas a objetos datetime para comparar
            remote_date = self.parking_db._parse_to_local_date(remote_last_updated_at)
            local_date = self.parking_db._parse_to_local_date(local_last_updated_at)

            # Comparar fechas
            if remote_date > local_date:
                self.logger.info(f"Remote update detected for identifier: {identifier}. Updating local data...")
                self.parking_db.update_parking(self.parking_db.map_to_update_db(payload))
                self.logger.info("Local parking updated successfully.")
            else:
                self.logger.info("No updates needed. Local data is up to date.")

        except Exception as e:
            self.logger.error(f"Unable to process incoming parking message: {e}")
            
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker")
        else:
            self.logger.error(f"Error connection to MQTT broker, error code: {rc}")

    def on_publish(self, client, userdata, mid):
        self.logger.info(f"Message published successfully with ID: {mid}")

    def on_disconnect(self, client, userdata, rc):
        self.logger.warning("Desconnected from broker")

    def publish_parking_update(self, available, identifier, plate):
        last_updated_at = datetime.now().isoformat()
        self.parking_db.update_parking_availability(identifier, available, plate, last_updated_at)  # Guarda en BD local

        payload = json.dumps({
            "entityId": Config.ENTITY_ID, 
            "identifier": identifier, 
            "currentLicensePlate": plate, 
            "available": available,
            "lastUpdatedAt": last_updated_at
            })

        # Publicar mensaje
        result, mid = self.client.publish(EVENTS_TOPIC, payload, qos=2)

        if result == mqtt.MQTT_ERR_SUCCESS:
            self.parking_db.update_parking_sync(identifier)
        else:
            self.logger.error(f"Error sending message to MQTT broker: {result}")
