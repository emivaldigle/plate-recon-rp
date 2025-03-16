from src.processing.detector import PlateDetector
from src.database.database_connector import DatabaseConnector
from src.database.synchronizer import Synchronizer


async def main():
    # Inicializar base de datos
    db = DatabaseConnector()
    db.initialize_database()

    # Crear datos iniciales
    synchronizer = Synchronizer()
    await synchronizer.sync()

    # Iniciar detector
    detector = PlateDetector()
    detector.detect_plates()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())