from src.config import Config
from src.database.models import ParkingModel
from src.database.models import _parse_to_local_date
from datetime import datetime
import logging
from src.http.synchronous_api_client import SynchronousAPIClient

class ParkingService:
    def __init__(self):
        """Initialize the ParkingService class."""
        self.logger = logging.getLogger(__name__)
        self.db_client = ParkingModel()

    def sync_parking(self):
        """
        Sync parking data from the remote API to the local database.
        This method fetches updated parking data from the API and updates or creates records in the database.
        """

        last_updated_parking = _parse_to_local_date(self.db_client.find_last_sync_parking()[8])

        self.logger.info(f"Last parking updated at {last_updated_parking}")
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        params = {"date": last_updated_parking}

        try:
            remote_parking = api_client.get(f"/parking/find-by-entity/{Config.ENTITY_ID}/date", params)
            if remote_parking:
                self._process_remote_parking(remote_parking)
        except Exception as ex:
            self.logger.error(f"Unable to connect to remote API, skipping... {ex}")

    def load_remote_parking(self):
        """
        Load parking lots from the remote API into the local database.
        If no local parking lots exist, it syncs all parking lots from the API.
        """
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            self.logger.info("Attempting to do initial load on parking lots")
            last_sync_parking = self.db_client.find_last_sync_parking()

            if last_sync_parking is None:
                self.logger.info("No parking lots found locally. Syncing all parking lots.")
                parking_lots = api_client.get(f"/parking/find-by-entity/{Config.ENTITY_ID}")
                self.insert_parking(parking_lots)
                self.logger.info(f"Created {len(parking_lots)} parking lots.")
            else:
                self.logger.info("No need to load, initial data already loaded")
        except Exception as ex:
            self.logger.error(f"Unable to load parking lots: {ex}")

    def _get_last_updated_parking(self):
        """
        Retrieve the last updated parking record from the database.
        If no record exists, return the current time.

        Returns:
            datetime: The last updated timestamp or the current time.
        """
        UPDATED_AT_INDEX = 8
        db_parking = self.db_client.find_last_sync_parking()

        if db_parking is not None:
            last_updated_parking = db_parking[UPDATED_AT_INDEX]
            last_updated_parking = _parse_to_local_date(last_updated_parking)
        
        else:
            last_updated_parking = datetime.now()

        return last_updated_parking

    def _process_remote_parking(self, remote_parking):
        """
        Process remote parking data by comparing timestamps and updating or creating records in the database.

        Args:
            remote_parking (list): List of parking records fetched from the API.
        """
        for parking in remote_parking:
            existing_parking = self.db_client.find_by_id(parking.get("id"))
            api_date_str = parking.get("lastUpdatedAt")
            api_date = datetime.strptime(api_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            if existing_parking:
                local_date = _parse_to_local_date(existing_parking[8])
                if api_date > local_date:
                    self.logger.info("Updating local parking")
                    self.db_client.update_parking(self.db_client.map_to_update_db(parking))
                else:
                    self.logger.info("Parking is up to date")
            else:
                self.db_client.create_parking(self.db_client.map_to_insert_db(parking))


    
    def insert_parking(self, parking_lots):
        """
        Insert multiple parking lots into the database.

        Args:
            parking_lots (list): List of parking data to be inserted.
        """
        for parking in parking_lots:
            db_parking = self.db_client.map_to_insert_db(parking)
            self.db_client.create_parking(db_parking)