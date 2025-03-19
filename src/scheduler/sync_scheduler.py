from apscheduler.schedulers.background import BackgroundScheduler
import time
import threading
import logging
from src.config import Config
from src.services.parking_service import ParkingService
from src.database.models import ConfigModel

class SyncScheduler:
    def __init__(self):
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.scheduler = BackgroundScheduler()

    def job(self):
        self.logger.info("Starting scheduled synchronization ...")
        parking_service = ParkingService()
        parking_service.sync_parking()

    def start_scheduler(self):
        config_db = ConfigModel()
        entity_id = Config.ENTITY_ID
        sync_interval = 1 #config_db.find_config(entity_id)[3]

        if not isinstance(sync_interval, int) or sync_interval <= 0:
            self.logger.error("Invalid sync interval. Defaulting to 5 minutes.")
            sync_interval = 5  # Valor predeterminado

        self.logger.info(f"Scheduler configured to run every {sync_interval} minutes")
        self.scheduler.add_job(self.job, 'interval', minutes=sync_interval)
        self.scheduler.start()
        self.running = True

    def stop_scheduler(self):
        self.scheduler.shutdown()
        self.running = False
