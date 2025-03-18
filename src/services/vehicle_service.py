from src.config import Config
from src.database.models import VehicleModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class VehicleService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_remote_vehicles(self):
        entity_id = Config.ENTITY_ID
        db_client = VehicleModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            self.logger.info("Attempting to sync vehicles")

            # Aquí buscamos el último vehículo sincronizado de manera síncrona
            last_sync_vehicle = db_client.find_last_sync_vehicle()

            if last_sync_vehicle is None:
                self.logger.info("No vehicles found locally. Loading all vehicles.")
                vehicles = api_client.get(f"/vehicles/find-by-entity/{entity_id}")  # Llamada síncrona
                self.insert_vehicles(vehicles)  # Inserción síncrona
                self.logger.info(f"Created {len(vehicles)} vehicles.")
            else:
                self.logger.info("No need to load, everything was created successfully")

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
                vehicle.get("createdAt"),
                vehicle.get("lastUpdatedAt")
            )
            # Aquí insertamos de manera síncrona
            db_client.create_vehicle(db_vehicle)

