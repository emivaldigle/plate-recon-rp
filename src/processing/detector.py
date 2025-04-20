import time
import logging
import re
from threading import Thread  # For handling background blinking
from picamera2 import Picamera2
import cv2
from fast_alpr import ALPR
from src.config import Config
from src.processing.gpio_controller import GPIOController
from src.messaging.mqtt_event_service import MqttEventService
from src.messaging.mqtt_parking_service import MqttParkingService
from src.services.access_service import AccessService
from src.services.event_service import EventService

class PlateDetector:
    DETECTOR_MODEL = "yolo-v9-t-384-license-plate-end2end"
    OCR_MODEL = "global-plates-mobile-vit-v2-model"
    CAMERA_RESOLUTION = (1920, 1080)
    CAMERA_FORMAT = "RGB888"
    CAMERA_INIT_DELAY = 1  # seconds

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gpio = GPIOController()
        self.alpr = ALPR(detector_model=self.DETECTOR_MODEL, ocr_model=self.OCR_MODEL)
        self.picam = self._initialize_camera()
        self.processing_led_active = False

    def _initialize_camera(self):
        """Configures and starts the camera."""
        picam = Picamera2()
        config = picam.create_preview_configuration(main={"size": self.CAMERA_RESOLUTION, "format": self.CAMERA_FORMAT})
        picam.configure(config)
        picam.start()

        time.sleep(self.CAMERA_INIT_DELAY)
        self.logger.info("Camera activated (PyCamera2 display)")
        return picam

    def detect_plates(self, max_frames=None):
        """Main loop for detecting license plates."""
        self._start_processing()
        frame_count = 0

        try:
            while not max_frames or frame_count < max_frames:
                frame = self._capture_frame()
                if frame is None:
                    break
                    # Convertir el frame a ASCII
                results = self.alpr.predict(frame)
                self._process_results(results)
                
                frame_count += 1
                
            self.logger.info(f"Stopping after {frame_count} frames, waiting 5 s to start over....")
            time.sleep(5) # 
        finally:
            self._cleanup()

    def _capture_frame(self):
        """Captures a frame from the camera."""
        try:
            return self.picam.capture_array()
        except Exception as e:
            self.logger.error(f"Error capturing frame: {e}")
            return None

    def _process_results(self, results):
        """Processes the ALPR results."""
        for result in results:
            plate = result.ocr.text
            detection_confidence = result.detection.confidence
            ocr_confidence = result.ocr.confidence
            self.logger.debug(f"Plate detected: {result}")

            if self._is_valid_plate(plate, detection_confidence, ocr_confidence):
                self._handle_plate_detection(plate)

    def _is_valid_plate(self, plate, detection_confidence, ocr_confidence):
        """Checks if the detected plate meets the confidence thresholds and validation rules."""
        if ocr_confidence > Config.OCR_CONFIDENCE and detection_confidence > Config.DETECTION_CONFIDENCE:
            if self.validate_plate(plate):
                self.logger.info(f"Valid plate detected: {plate} (OCR: {ocr_confidence}, Detection: {detection_confidence})")
                return True
        return False

    def _handle_plate_detection(self, plate):
        """Handles the actions after detecting a valid plate."""
        access_service = AccessService()
        mqtt_event_service = MqttEventService()
        mqtt_parking_service = MqttParkingService()
        event_service = EventService()
        
        last_event_type = event_service.find_last_registered_event_type(plate)
        is_authorized, parking_identifier = access_service.is_vehicle_authorized(plate, last_event_type)
        self.logger.info(f"Parking identifier: {parking_identifier}")
        
        event_type = "EXIT" if last_event_type == "ACCESS" else "ACCESS"
        
        if is_authorized:
            self._grant_access(mqtt_event_service, mqtt_parking_service, event_type, plate, parking_identifier)
        else:
            self._deny_access(mqtt_event_service, plate, event_type)


    def _grant_access(self, mqtt_event_service, mqtt_parking_service, event_type, plate, parking_identifier):
        """Handles access granting logic."""
        self.gpio.led_off("processing")
        mqtt_event_service.publish_event(event_type, plate)
        available = event_type == "EXIT" or event_type is None
        mqtt_parking_service.publish_parking_update(available, parking_identifier, plate)
        self.gpio.led_on("access_granted")


    def _deny_access(self, mqtt_event_service, plate, event_type):
        """Handles access denial logic."""
        self.gpio.led_off("processing")
        final_event_type = f"DENIED_{event_type}"
        mqtt_event_service.publish_event(final_event_type, plate)
        self.gpio.led_on("access_denied")

    def _start_processing(self):
        """Activates processing LED and initializes state."""
        self.processing_led_active = True
        self.gpio.led_on("processing")
        self.logger.info("Starting plate detection...")

    def _cleanup(self):
        """Stops the camera and turns off LEDs."""
        try:
            self.picam.stop()
            self.picam.close()
        except Exception as e:
            self.logger.debug("Unable to stop camera: {e}")
        
        self.gpio.led_off("processing")
        self.gpio.led_off("access_granted")
        self.gpio.led_off("access_denied")

    def validate_plate(self, plate):
        """Validates the license plate format."""
        for plate_type, pattern in Config.PATTERN_MAP.items():
            if re.match(pattern, plate):
                self.logger.info(f"License plate matched type: {plate_type}")
                return True
        return False

