import cv2
import logging
from fast_alpr import ALPR
from src.config import Config
from src.gpio_controller import GPIOController
import inspect
import time

class PlateDetector:
    def __init__(self):
        self.alpr = ALPR(
            detector_model="yolo-v9-t-384-license-plate-end2end",
            ocr_model="global-plates-mobile-vit-v2-model"
        )
        self.gpio = GPIOController()
        self.logger = logging.getLogger(__name__)
        print(inspect.getfile(Config))  # Esto mostrará la ubicación del archivo Config
        # Configurar fuente (video o stream)
        if Config.SOURCE_TYPE == "CAMERA":
            # Usamos OpenCV para capturar desde la cámara directamente
            self.cap = cv2.VideoCapture(0)  # Cámara por defecto
            if not self.cap.isOpened():
                self.logger.error("Error al abrir la cámara.")
                raise Exception("No se pudo abrir la cámara")
            self.logger.info("Modo cámara habilitado...")
        elif Config.SOURCE_TYPE == "VIDEO":
            self.cap = cv2.VideoCapture(Config.VIDEO_PATH)
            self.logger.info("Modo video habilitado...")
        else:
            self.cap = cv2.VideoCapture(Config.STREAM_URL)
            self.logger.info("Modo stream habilitado...")

        if hasattr(self, 'cap'):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def detect_plates(self, max_frames=None):
        self.gpio.led_on("processing")  # LED azul encendido
        self.logger.info("Iniciando detección de patentes...")
        frame_count = 0  # Contador de frames procesados

        while True:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error("Error al leer el frame")
                break

            # Detectar patentes
            results = self.alpr.predict(frame)
            self.logger.debug(f"Resultados crudos: {results}")  # Log de datos sin filtrar

            for result in results:
                text = result.ocr.text
                confidence = result.ocr.confidence

                # Validar formato chileno (2 letras + 4 números)
                self.logger.info(f"Placa válida detectada: {text} (Confianza: {confidence:.2f})")

                # Enviar a servidor HTTP y controlar LEDs
                if confidence > Config.OCR_CONFIDENCE:
                    self.gpio.led_on("access_granted")  # LED verde
                    self.logger.info("Acceso concedido")
                else:
                    self.gpio.led_on("access_denied")   # LED rojo
                    self.logger.warning("No suficiente confianza")

                # Dibujar en el frame
                bbox = result.detection.bounding_box
                cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (bbox.x1, bbox.y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.imshow("Detector", frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

            # Incrementar contador de frames
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                self.logger.info(f"Procesamiento detenido después del frame número {frame_count}")
                break

        self.cap.release()
        self.gpio.cleanup()  # Limpiar GPIO
        cv2.destroyAllWindows()
