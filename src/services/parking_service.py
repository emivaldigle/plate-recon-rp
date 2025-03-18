from src.config import Config
from src.database.models import ParkingModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class ParkingService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_remote_parking(self):
        entity_id = Config.ENTITY_ID
        db_client = ParkingModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            self.logger.info("Attempting to do initial load on parking lots")
            
            # Aquí buscamos el último vehículo sincronizado de manera síncrona
            last_sync_parking = db_client.find_last_sync_parking()

            if last_sync_parking is None:
                self.logger.info("No parking lots found locally. Syncing all parking lots.")
                parking_lots = api_client.get(f"/parking/find-by-entity/{entity_id}")  # Llamada síncrona
                self.insert_vehicles(parking_lots)  # Inserción síncrona
                self.logger.info(f"Created {len(parking_lots)} parking lots.")
            else:
                self.logger.info("No need to load, everything was created successfully")

        except Exception as ex:
            self.logger.error(f"Unable to load parking lots: {ex}")

    def insert_vehicles(self, parking_lots):
        db_client = ParkingModel()
        for parking in parking_lots:
            db_parking = (
                parking.get("id"),
                parking.get("user", {}).get("id") if parking.get("user") else None,
                parking.get("identifier"),
                parking.get("currentLicensePlate") if parking.get("currentLicensePlate") else None,
                parking.get("isForVisit"),
                parking.get("available"),
                parking.get("createdAt"),
                parking.get("expiration_date") if parking.get("expiration_date") else None,
                parking.get("lastUpdatedAt")
            )
            db_client.create_parking(db_parking)

