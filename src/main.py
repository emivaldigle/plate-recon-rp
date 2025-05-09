from src.processing.detector import PlateDetector
from src.database.database_connector import DatabaseConnector
from src.database.data_loader import Dataloader
from src.scheduler.sync_scheduler import SyncScheduler
from src.processing.gpio_controller import GPIOController
from src.messaging.mqtt_parking_service import MqttParkingService
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
    detector.detect_plates(30)
    time.sleep(3)

def monitor_motion_in_background(gpio_controller):
    """
    Monitor the motion sensor in a separate thread.
    This ensures the main program remains responsive.
    """
    try:
        print("Starting motion sensor monitoring...")
        gpio_controller.monitor_motion_sensor(callback=on_motion_detected)
    except KeyboardInterrupt:
        print("Stopping motion sensor monitoring...")
    except Exception as e:
        print(f"Error in motion sensor monitoring: {e}")


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
    # Initialize mqtt topic subscriptions
        mqtt_parking_service = MqttParkingService()
        mqtt_parking_service.subscribe_on_topic()
        while True:
            time.sleep(1)  # Prevent excessive CPU usage
    except KeyboardInterrupt:
        print("Program stopped.")


if __name__ == "__main__":
    main()
