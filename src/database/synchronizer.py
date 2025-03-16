import logging
from datetime import datetime
from src.services.entity_config_service import EntityConfigService
from src.services.vehicle_service import VehicleService
from src.services.parking_service import ParkingService

class Synchronizer:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Hacemos la función 'sync' asíncrona
    async def sync(self):
        self.logger.info(f'Starting sync at {datetime.now()}')
        
        # Instanciamos el servicio de configuración
        configService = EntityConfigService()
        
        # Llamamos a sync_config de forma asíncrona
        configs = await configService.sync_config()
        
        # Instanciamos el servicio de vehículos
        vehicleService = VehicleService()
        sync_interval = configs.get("syncIntervalMinutes")
        # Llamamos a sync_vehicles de forma asíncrona, pasándole el parámetro necesario
        await vehicleService.sync_vehicles(sync_interval)

        parkingService = ParkingService()

        await parkingService.sync_parking(sync_interval)

# Método principal para ejecutar la sincronización
async def main():
    synchronizer = Synchronizer()
    await synchronizer.sync()  # Llamamos a 'sync' de forma asíncrona

# Ejecutamos el ciclo de eventos de asyncio para ejecutar el código asíncrono
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
