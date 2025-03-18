import schedule
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

    def job(self):
        self.logger.info("Starting scheduled synchronization ...")

    def start_scheduler(self):
        config_db = ConfigModel()
        entity_id = Config.ENTITY_ID
        sync_interval = config_db.find_config(entity_id)[3]
        self.logger.info(f"Scheduler configured to run every {sync_interval} minutes")
        self.running = True
        schedule.every(sync_interval).minutes.do(self.job)

        # Ejecutar el scheduler en un hilo separado
        def run():
            while self.running:
                parking_service = ParkingService()
                parking_service.sync_parking()
                schedule.run_pending()
                time.sleep(1)

        threading.Thread(target=run, daemon=True).start()

    def stop_scheduler(self):
        self.running = False