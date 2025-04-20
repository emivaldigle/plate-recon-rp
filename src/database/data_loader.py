import logging
from datetime import datetime
from src.services.vehicle_service import VehicleService
from src.services.parking_service import ParkingService
from src.services.entity_config_service import EntityConfigService

class Dataloader:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_data(self):
        self.logger.info(f'Starting data load at {datetime.now()}')
        
        config_service = EntityConfigService()
        config_service.load_remote_config()

        vehicle_service = VehicleService()
        vehicle_service.load_remote_vehicles()

        parking_service = ParkingService()
        parking_service.load_remote_parking()


        