from src.config import Config
from src.database.models import VehicleModel
from src.database.models import ParkingModel
import logging
from src.http.synchronous_api_client import SynchronousAPIClient  # Usamos el cliente síncrono

class AccessService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def is_vehicle_authorized(self, plate, last_event_type):
        parking_db = ParkingModel()
        vehicle_db = VehicleModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)
        try:
            self.logger.info(f"Requesting authorization for plate {plate}")
            vehicle = vehicle_db.find_vehicle_by_plate(plate)
            if vehicle is None:
                self.logger.info(f"Vehicle with license plate {plate} not found locally")
                entityId = Config.ENTITY_ID
                try:
                    remote_access = api_client.get(f"/access/entity/{entityId}/plate/{plate}")
                    if remote_access is not None:
                        return remote_access.get("authorized"), remote_access.get("identifier")
                except Exception as ex:
                    self.logger.warning("Unable to check authorization remotely")
            else:
                self.logger.info(f"Vehicle {vehicle} found locally, proceeding with validation")
                user_id = vehicle[1]
                self.logger.info(f"Vehicle user_id {user_id} found locally, proceeding with validation")

                parking = parking_db.find_by_user_id(user_id)
                if parking is None:
                    self.logger.warning("No parking available found locally, checking remotely...")
                    try:
                        remote_parking = api_client.get(f"/parking/find-by-user/{user_id}")
                        first_available = next((parking for parking in remote_parking if parking.get("available")), None)
                        if (first_available):
                            return True, first_available.get("parkingIdentifier")
                        else:
                            return False, remote_parking[0].get("parkingIdentifier")
                    except Exception as ex:
                        self.logger.warning(f"Unable to check remote parking... {ex}")
                else:
                    authorized = parking[5]
                    if authorized == False and last_event_type == "ACCESS":
                        authorized = True
                    self.logger.info(f"Authorization obtained locally is_authorized: {authorized}")
                    return  authorized, parking[2]
            return False, None    
        except Exception as ex:
            self.logger.error(f"Unable to validate access {ex}")
            return False, None
