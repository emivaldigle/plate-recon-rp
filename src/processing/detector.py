import cv2
import logging
from fast_alpr import ALPR
from src.config import Config
from src.processing.gpio_controller import GPIOController
import time
from threading import Thread  # Para manejar parpadeos en segundo plano

class PlateDetector:
    def __init__(self):
        self.alpr = ALPR(
            detector_model="yolo-v9-t-384-license-plate-end2end",
            ocr_model="global-plates-mobile-vit-v2-model"
        )
        self.gpio = GPIOController()
        self.logger = logging.getLogger(__name__)

        # Configurar camara
        if Config.SOURCE_TYPE == "CAMERA":
            from picamera2 import Picamera2
            self.picam = Picamera2()
            config = self.picam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
            self.picam.configure(config)
            self.picam.start_preview()
            self.picam.start()
            time.sleep(2)
            self.logger.info("Camera activated (OpenCV display)")
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
                    frame = self.picam.capture_array()
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        self.logger.error("Failed to read frame")
                        break
                # 3 letras + 1 numero o 4 letras + 1 numero o 4 letras + 2 numeros
                # Procesar frame
                results = self.alpr.predict(frame)
                for result in results:
                    text = result.ocr.text
                    confidence = result.detection.confidence
                    ocr_confidence = result.ocr.confidence
                    # Detener parpadeo azul y manejar LEDs
                    # self.gpio.led_off("processing")  # Apaga y detiene el thread <button class="citation-flag" data-index="7">
                    self.logger.debug(f"Plate detected {result}")

                    if ocr_confidence > Config.OCR_CONFIDENCE and confidence > Config.DETECTION_CONFIDENCE:
                        self.logger.info(f"Plate detected with text: {text}, ocr confidence {ocr_confidence} detection confidence {confidence}")
                        self.gpio.blink_led("access_granted", interval=0.5, duration=2)  # Parpadea 2s <button class="citation-flag" data-index="7">
                    else:
                        self.gpio.blink_led("access_denied", interval=0.5, duration=2)   # Parpadea 2s <button class="citation-flag" data-index="7">

                        # Dibujar en el frame
                        bbox = result.detection.bounding_box
                        cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 2)
                        cv2.putText(frame, text, (bbox.x1, bbox.y1-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # Mostrar frame
                cv2.imshow("Detector", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Control de frames maximos
                frame_count += 1
                if max_frames and frame_count >= max_frames:
                    self.logger.info(f"Stopping after {frame_count} frames")
                    break

        finally:
            # Detener parpadeos y limpiar
            self.processing_led_active = False
            self.gpio.cleanup()
            if Config.SOURCE_TYPE == "CAMERA":
                self.picam.stop_preview()
                self.picam.stop()
            else:
                self.cap.release()
            cv2.destroyAllWindows()
