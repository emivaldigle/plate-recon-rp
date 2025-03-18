from src.config import Config
from src.database.models import ParkingModel
from datetime import datetime
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class ParkingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def sync_parking(self):
        UPDATED_AT_INDEX = 8
        db_client = ParkingModel()
        db_parking = db_client.find_last_sync_parking()
        last_updated_parking = db_parking[UPDATED_AT_INDEX] if db_parking is not None else datetime.now()
        self.logger.info(f"Last parking updated at {last_updated_parking}")
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        params = {"date": last_updated_parking}
        try:
            remote_parking = api_client.get("/parking/find-by-entity/" + Config.ENTITY_ID + "/date", params)
            if remote_parking is not None:
                    for parking in remote_parking:
                        existing_parking = db_client.find_by_id(parking["id"])
                        if existing_parking:
                            # Comparar fechas de última actualización
                            api_date_str = parking.get("lastUpdatedAt")
                            # Convertir la fecha local a datetime si es una cadena
                            local_date_str = existing_parking[UPDATED_AT_INDEX]
                            if isinstance(local_date_str, str):
                                local_date = datetime.strptime(local_date_str, "%Y-%m-%d %H:%M:%S")
                            else:
                                local_date = local_date_str  # Ya es un objeto datetime
                            # Convertir a datetime
                            api_date = datetime.strptime(api_date_str, "%Y-%m-%d %H:%M:%S")
                            if api_date > local_date:
                                self.logger.info("updating local parking")
                                db_client.update_parking(parking)
                        else:
                            # Insertar si no existe
                            db_client.create_parking(parking)
        except Exception as ex:
            self.logger.error(f"Unable to connect to remote api, skipping...{ex}")

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

