from datetime import datetime, timedelta
from src.config import Config
from src.database.models import VehicleModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class VehicleService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def sync_vehicles(self, sync_interval):
        entity_id = Config.ENTITY_ID
        db_client = VehicleModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            self.logger.info("Attempting to sync vehicles")

            # Aquí buscamos el último vehículo sincronizado de manera síncrona
            last_sync_vehicle = db_client.find_last_sync_vehicle()

            if last_sync_vehicle is None:
                self.logger.info("No vehicles found locally. Syncing all vehicles.")
                vehicles = api_client.get(f"/vehicles/find-by-entity/{entity_id}")  # Llamada síncrona
                self.insert_vehicles(vehicles)  # Inserción síncrona
                self.logger.info(f"Synced {len(vehicles)} vehicles.")
            else:
                self.logger.debug(f"last sync record {last_sync_vehicle}")
                last_sync_record = datetime.strptime(last_sync_vehicle[6], '%Y-%m-%d %H:%M:%S.%f')
                now = datetime.now()
                time_diff = now - last_sync_record
                self.logger.info(f"Found vehicles, last sync was {last_sync_record} and time diff {time_diff}")

                if time_diff > timedelta(minutes=sync_interval):
                    self.logger.info("Sync interval has passed. Updating vehicles.")
                    vehicles = api_client.get(f"/vehicles/find-by-entity/{entity_id}")  # Llamada síncrona
                    self.update_vehicles(vehicles)  # Actualización síncrona
                    self.logger.info(f"Updated {len(vehicles)} vehicles.")
                else:
                    self.logger.info("No need to sync, everything up to date")

        except Exception as ex:
            self.logger.error(f"Unable to load configuration or sync vehicles: {ex}")

    def insert_vehicles(self, vehicles):
        db_client = VehicleModel()
        for vehicle in vehicles:
            db_vehicle = (
                vehicle.get("id"),
                vehicle.get("plate"),
                vehicle.get("vehicleType"),
                vehicle.get("user").get("id"),
                vehicle.get("user").get("type"),
                vehicle.get("created_at")
            )
            # Aquí insertamos de manera síncrona
            db_client.create_vehicle(db_vehicle)

    def update_vehicles(self, vehicles):
        db_client = VehicleModel()
        for vehicle in vehicles:
            db_vehicle = (
                vehicle.get("plate"),
                vehicle.get("vehicleType"),
                vehicle.get("user").get("id"),
                vehicle.get("user").get("type"),
                vehicle.get("created_at"),
                vehicle.get("id")
            )
            # Aquí actualizamos de manera síncrona
            db_client.update_vehicle(db_vehicle)
