import cv2
import logging
from fast_alpr import ALPR
from src.config import Config
from src.processing.gpio_controller import GPIOController
import time
from threading import Thread  # Para manejar parpadeos en segundo plano
from src.messaging.mqtt_event_service import MqttEventService
from src.messaging.mqtt_parking_service import MqttParkingService
from src.services.access_service import AccessService
from src.services.event_service import EventService

class PlateDetector:
    def __init__(self):
        self.alpr = ALPR(
            detector_model="yolo-v9-t-384-license-plate-end2end",
            ocr_model="global-plates-mobile-vit-v2-model"
        )
        self.gpio = GPIOController()
        self.logger = logging.getLogger(__name__)

        # Configurar cámara
        if Config.SOURCE_TYPE == "CAMERA":
            from picamera2 import Picamera2
            self.picam = Picamera2()
            config = self.picam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
            self.picam.configure(config)
            self.picam.start()
            time.sleep(2)  # Esperar a que la cámara se inicie
            self.logger.info("Camera activated (PyCamera2 display)")
        else:
            self.cap = cv2.VideoCapture(Config.VIDEO_PATH if Config.SOURCE_TYPE == "VIDEO" else Config.STREAM_URL)

    def detect_plates(self, max_frames=None):
        # Iniciar parpadeo azul (processing) en segundo plano
        self.processing_led_active = True
        self.gpio.blink_led("processing", interval=0.5)

        self.logger.info("Starting plate detection...")
        frame_count = 0

        try:
            while True:
                # Capturar frame
                if Config.SOURCE_TYPE == "CAMERA":
                    try:
                        frame = self.picam.capture_array()  # Captura el frame como un array NumPy
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convierte de RGB a BGR para OpenCV
                  
                    except Exception as e:
                        self.logger.error(f"Error capturing frame: {e}")
                        break
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        self.logger.error("Failed to read frame")
                        break

                # Mostrar el frame en una ventana de OpenCV
                #cv2.imshow("Camera Preview", frame)
                self.logger.debug(f"Frame captured with shape: {frame.shape}")  
                # Salir si se presiona la tecla 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Procesamiento adicional (ALPR, etc.)
                results = self.alpr.predict(frame)
                for result in results:
                    plate = result.ocr.text
                    confidence = result.detection.confidence
                    ocr_confidence = result.ocr.confidence
                    self.logger.debug(f"Plate detected {result}")

                    if ocr_confidence > Config.OCR_CONFIDENCE and confidence > Config.DETECTION_CONFIDENCE:
                        self.logger.info(f"Plate detected with text: {plate}, ocr confidence {ocr_confidence} detection confidence {confidence}")
                        access_service = AccessService()
                        mqtt_event_service = MqttEventService()
                        mqtt_parking_service = MqttParkingService()
                        event_service = EventService()
                        last_event_type = event_service.find_last_registered_event_type(plate)
                        is_authorized, parking_identifier = access_service.is_vehicle_authorized(plate, last_event_type)
                        if is_authorized:
                            # open gate
                            event_type = "EXIT" if last_event_type is not None and last_event_type == "ACCESS" else "ACCESS"
                            mqtt_event_service.publish_event(event_type, plate)
                            available = True if event_type == "EXIT" else False
                            mqtt_parking_service.publish_parking_update(available, parking_identifier, plate)
                            self.gpio.blink_led("access_granted", interval=0.5, duration=2)
                        else:
                            last_event_type = event_service.find_last_registered_event_type(plate)
                            event_type = "EXIT" if last_event_type is not None and last_event_type == "ACCESS" else "ACCESS"
                            self.gpio.blink_led("access_denied", interval=0.5, duration=2)
                            mqtt_event_service.publish_event("DENIED_" + event_type, plate)
                    else:
                        self.gpio.blink_led("access_denied", interval=0.5, duration=2)

                # Control de frames máximos
                frame_count += 1
                self.logger.info(f"frame count {frame_count}")
                if max_frames and frame_count >= max_frames:
                    self.logger.info(f"Stopping after {frame_count} frames")
                    break

        finally:
            # Detener parpadeos y limpiar
            if Config.SOURCE_TYPE == "CAMERA":
                self.picam.stop()
            else:
                self.cap.release()
            cv2.destroyAllWindows()
            

