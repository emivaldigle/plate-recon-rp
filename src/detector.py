import cv2
import logging
from fast_alpr import ALPR
from src.config import Config
from src.gpio_controller import GPIOController

class PlateDetector:
    def __init__(self):
        self.alpr = ALPR(
            detector_model="yolo-v9-t-384-license-plate-end2end",
            ocr_model="global-plates-mobile-vit-v2-model"
        )
        self.gpio = GPIOController()
        self.logger = logging.getLogger(__name__)
        
        # Configurar fuente (video o stream) <button class="citation-flag" data-index="1">
        if Config.SOURCE_TYPE == "VIDEO":
            self.cap = cv2.VideoCapture(Config.VIDEO_PATH)
        elif Config.SOURCE_TYPE == "STREAM":
            self.cap = cv2.VideoCapture(Config.STREAM_URL)
        else:
            raise ValueError("SOURCE_TYPE debe ser 'VIDEO' o 'STREAM'")

    def detect_plates(self, max_frames=None):
        self.gpio.led_on("processing")  # LED azul encendido <button class="citation-flag" data-index="6">
        self.logger.info("Starting plate detection...")
        frame_count = 0  # Contador de frames procesados

        while True:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error("Error reading the frame, restaring the video now" if Config.SOURCE_TYPE == "VIDEO" else "Stream not available")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Detectar patentes
            
            results = self.alpr.predict(frame)
            self.logger.debug(f"Raw results: {results}")  # Log de datos sin filtrar <button class="citation-flag" data-index="2">
            
            for result in results:
                text = result.ocr.text
                confidence = result.ocr.confidence
                
                # Validar formato chileno (2 letras + 4 números) <button class="citation-flag" data-index="1">
                self.logger.info(f"Valid plate detected: {text} (Confidence: {confidence:.2f})")
                
                # Enviar a servidor HTTP y controlar LEDs
                if confidence > Config.OCR_CONFIDENCE:
                    self.gpio.led_on("access_granted")  # LED verde <button class="citation-flag" data-index="6">
                    self.logger.info("Access granted")
                else:
                    self.gpio.led_on("access_denied")   # LED rojo <button class="citation-flag" data-index="6">
                    self.logger.warning("Not enough confidence")
                
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
                self.logger.info(f"Processing stopped after frame number {frame_count}")
                break
        
        self.cap.release()
        self.gpio.cleanup()  # Limpiar GPIO <button class="citation-flag" data-index="6">
        cv2.destroyAllWindows()
        