from src.detector import PlateDetector
from src.config import Config

if __name__ == "__main__":
    # Configurar entorno
    Config.SOURCE_TYPE = "VIDEO"  # Cambiar a "STREAM" en producción <button class="citation-flag" data-index="1">
    Config.HTTP_SERVER_HOST = "http://mock-server:8000"  # Cambiar según entorno
    
    # Iniciar detector
    detector = PlateDetector()
    detector.detect_plates()