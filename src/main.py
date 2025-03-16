from src.processing.detector import PlateDetector
from src.database.database_connector import DatabaseConnector
from src.database.synchronizer import Synchronizer


def main():
    db = DatabaseConnector()
    db.initialize_database()

    synchronizer = Synchronizer()
    synchronizer.initialize()

    detector = PlateDetector()
    detector.detect_plates()

if __name__ == "__main__":
    main()