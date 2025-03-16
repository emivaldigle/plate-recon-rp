import logging
from datetime import datetime
from src.services.entity_config_service import EntityConfigService
from src.services.vehicle_service import VehicleService
from src.services.parking_service import ParkingService

class Synchronizer:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Hacemos la función 'sync'
    def initialize(self):
        self.logger.info(f'Starting sync at {datetime.now()}')
        
        configService = EntityConfigService()

        configs = configService.sync_config()
        
        vehicleService = VehicleService()
        sync_interval = configs.get("syncIntervalMinutes")
        vehicleService.sync_vehicles(sync_interval)

        parkingService = ParkingService()

        parkingService.sync_parking(sync_interval)
