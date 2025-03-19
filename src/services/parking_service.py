from src.config import Config
from src.database.models import ParkingModel
from datetime import datetime
import logging
from src.http.synchronous_api_client import SynchronousAPIClient

class ParkingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def sync_parking(self):
        UPDATED_AT_INDEX = 8
        db_client = ParkingModel()
        db_parking = db_client.find_last_sync_parking()
        
        # Asegurar que la fecha es un objeto datetime
        if db_parking is not None:
            last_updated_parking = db_parking[UPDATED_AT_INDEX]
            if isinstance(last_updated_parking, str):
                last_updated_parking = datetime.strptime(last_updated_parking, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            last_updated_parking = datetime.now()
        
        self.logger.info(f"Last parking updated at {last_updated_parking}")
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        params = {"date": last_updated_parking.strftime("%Y-%m-%d %H:%M:%S")}
        
        try:
            remote_parking = api_client.get(f"/parking/find-by-entity/{Config.ENTITY_ID}/date", params)
            if remote_parking:
                for parking in remote_parking:
                    existing_parking = db_client.find_by_id(parking["id"])
                    
                    api_date_str = parking.get("lastUpdatedAt")
                    api_date = datetime.strptime(api_date_str, "%Y-%m-%d %H:%M:%S")
                    if existing_parking:
                        local_date_str = existing_parking[UPDATED_AT_INDEX]
                        local_date = datetime.strptime(local_date_str, "%Y-%m-%dT%H:%M:%S") if isinstance(local_date_str, str) else local_date_str
                        
                        if api_date > local_date:
                            self.logger.info("Updating local parking")
                            db_client.update_parking(self.map_to_update_db(parking))
                    else:
                        db_client.create_parking(self.map_to_insert_db(parking))
        except Exception as ex:
            self.logger.error(f"Unable to connect to remote API, skipping... {ex}")

    def load_remote_parking(self):
        entity_id = Config.ENTITY_ID
        db_client = ParkingModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            self.logger.info("Attempting to do initial load on parking lots")
            last_sync_parking = db_client.find_last_sync_parking()

            if last_sync_parking is None:
                self.logger.info("No parking lots found locally. Syncing all parking lots.")
                parking_lots = api_client.get(f"/parking/find-by-entity/{entity_id}")
                self.insert_parking(parking_lots)
                self.logger.info(f"Created {len(parking_lots)} parking lots.")
            else:
                self.logger.info("No need to load, everything was created successfully")
        except Exception as ex:
            self.logger.error(f"Unable to load parking lots: {ex}")

    def map_to_insert_db(self, parking):
        return(
        parking.get("id"),
        parking.get("user", {}).get("id") if parking.get("user") else None,
        parking.get("identifier"),
        parking.get("currentLicensePlate"),
        parking.get("isForVisit"),
        parking.get("available"),
        parking.get("createdAt"),
        parking.get("expirationDate") if parking.get("expirationDate") else None,
        parking.get("lastUpdatedAt")
        )
        
    def map_to_update_db(self, parking):
        return (
        parking.get("user", {}).get("id") if parking.get("user") else None,
        parking.get("identifier"),
        parking.get("currentLicensePlate"),
        parking.get("isForVisit"),
        parking.get("available"),
        parking.get("createdAt"),
        parking.get("expirationDate") if parking.get("expirationDate") else None,
        parking.get("lastUpdatedAt",
        parking.get("id"))
        )
    def insert_parking(self, parking_lots):
        db_client = ParkingModel()
        for parking in parking_lots:
            db_parking = (
                parking.get("id"),
                parking.get("user", {}).get("id") if parking.get("user") else None,
                parking.get("identifier"),
                parking.get("currentLicensePlate"),
                parking.get("isForVisit"),
                parking.get("available"),
                parking.get("createdAt"),
                parking.get("expiration_date"),
                parking.get("lastUpdatedAt")
            )
            db_client.create_parking(db_parking)
