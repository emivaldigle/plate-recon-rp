import logging
from datetime import datetime
from src.config import Config
from src.database.models import ConfigModel
from src.http.synchronous_api_client import SynchronousAPIClient  # Importamos el cliente síncrono

class EntityConfigService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def map_to_db_data(self, remote_data):
        return (
            Config.ENTITY_ID,
            remote_data.get("syncIntervalMinutes"),
            remote_data.get("parkingHoursAllowed"),
            remote_data.get("visitSizeLimit"),
            remote_data.get("parkingSizeLimit"),
            datetime.now(),
            remote_data.get("active")
        )

    def sync_config(self):
        entity_id = Config.ENTITY_ID
        db_client = ConfigModel()
        api_client = SynchronousAPIClient(Config.HTTP_SERVER_HOST)

        try:
            # Hacemos una llamada síncrona
            remote_data = api_client.get(f"/entities/configuration/{entity_id}")

            # Verificamos si la configuración ya existe
            if db_client.find_config(entity_id) is None:
                self.logger.info("Configuration not found, creating one")
                config_data = self.map_to_db_data(remote_data)
                self.logger.info(f"Saving config {config_data}")
                db_client.init_config(config_data)
                self.logger.info("Config created successfully")
            else:
                self.logger.info("Configuration found, updating...")
                self.logger.info(f'Remote data collected: {remote_data}')
                config_data = self.map_to_db_data(remote_data)
                config_data_without_id = config_data[1:]

                db_client.update_config(config_data_without_id, entity_id)
                self.logger.info("Config updated successfully")    

        except Exception as ex:
            self.logger.error(f"Unable to load configuration {ex}")

        return remote_data

