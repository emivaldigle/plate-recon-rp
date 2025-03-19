from src.processing.detector import PlateDetector
from src.database.database_connector import DatabaseConnector
from src.database.data_loader import Dataloader
from src.scheduler.sync_scheduler import SyncScheduler
from src.processing.gpio_controller import GPIOController
import threading
import time


def initialize_db():
    """Initialize the database with initial data."""
    db = DatabaseConnector()
    db.initialize_database()

    data_loader = Dataloader()
    data_loader.load_data()


def on_motion_detected():
    """Action to perform when motion is detected."""
    detector = PlateDetector()
    detector.detect_plates(100)
    time.sleep(10)


def monitor_motion_in_background(gpio_controller):
    """
    Monitor the motion sensor in a separate thread.
    This ensures the main program remains responsive.
    """
    try:
        gpio_controller.monitor_motion_sensor(callback=on_motion_detected)
    except KeyboardInterrupt:
        print("Stopping motion sensor monitoring...")


def main():
    # Initialize the database with initial data
    initialize_db()

    # Start the scheduler in a separate thread
    scheduler = SyncScheduler()
    scheduler_thread = threading.Thread(target=scheduler.start_scheduler, daemon=True)
    scheduler_thread.start()

    # Configure the GPIO controller
    gpio_controller = GPIOController()

    # Monitor the motion sensor in a background thread
    motion_monitor_thread = threading.Thread(
        target=monitor_motion_in_background, args=(gpio_controller,), daemon=True
    )
    motion_monitor_thread.start()

    # Keep the main program running
    try:
        while True:
            time.sleep(1)  # Prevent excessive CPU usage
    except KeyboardInterrupt:
        print("Program stopped.")


if __name__ == "__main__":
    main()
