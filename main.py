from src.detector import PlateDetector
from src.config import Config

if __name__ == "__main__":
    
    # Iniciar detector
    detector = PlateDetector()
    detector.detect_plates()