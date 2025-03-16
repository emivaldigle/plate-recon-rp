from src.config import Config
from datetime import datetime, timedelta
from src.database.models import ParkingModel
import logging
from src.http.asynchronous_api_client import AsynchronousAPIClient

class ParkingService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Convertimos esta función en asíncrona
    async def sync_parking(self, sync_interval):
        entity_id = Config.ENTITY_ID
        db_client = ParkingModel()
        api_client = AsynchronousAPIClient(Config.HTTP_SERVER_HOST)
        
        try:
            async with api_client as client:
                self.logger.info("Attempting to sync parking lots")
                
                # Aquí buscamos el último vehículo sincronizado de manera asíncrona
                last_sync_parking =  db_client.find_last_sync_parking()
                
                if last_sync_parking is None:
                    self.logger.info("No parking lots found locally. Syncing all parking lots.")
                    parking_lots = await client.get(f"/parking/find-by-entity/{entity_id}")
                    self.insert_vehicles(parking_lots)  # Llamamos a la inserción asíncrona
                    self.logger.info(f"Synced {len(parking_lots)} parking lots.")
                else:
                    self.logger.debug(f"last sync record {last_sync_parking}")
                    last_sync_record =  datetime.strptime(last_sync_parking[8], '%Y-%m-%d %H:%M:%S.%f') 
                    now = datetime.now()
                    
                    time_diff = now - last_sync_record
                    self.logger.info(f"Found parking lots, last sync was {last_sync_record} and time diff {time_diff}")

                    if time_diff > timedelta(minutes=sync_interval):
                        self.logger.info("Sync interval has passed. Updating parking lots.")
                        parking_lots = await client.get(f"/parking/find-by-entity/{entity_id}")
                        self.update_vehicles(parking_lots)  # Llamamos a la actualización asíncrona
                        self.logger.info(f"Updated {len(parking_lots)} parking lots.")
                    else:
                        self.logger.info("No need to sync, everything up to date")
        
        except Exception as ex:
            self.logger.error(f"Unable to load configuration or sync parking lots: {ex}")
    
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
                parking.get("created_at"),
                parking.get("expiration_date") if parking.get("expiration_date") else None  
            )
            db_client.create_parking(db_parking)

    def update_vehicles(self, parking_lots):
        db_client = ParkingModel()
        for parking in parking_lots:
            db_parking = (
                parking.get("user", {}).get("id") if parking.get("user") else None,  
                parking.get("identifier"), 
                parking.get("currentLicensePlate") if parking.get("currentLicensePlate") else None,  
                parking.get("isForVisit"),
                parking.get("available"),
                parking.get("created_at"),
                parking.get("expiration_date") if parking.get("expiration_date") else None, 
                parking.get("id")
            )

            db_client.update_parking(db_parking)
