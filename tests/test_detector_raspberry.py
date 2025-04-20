import unittest
from src.processing.detector import PlateDetector
from src.config import Config

class TestPlateDetectionRaspberry(unittest.TestCase):
    def setUp(self):
        # Configurar perfil RASPBERRY
        Config.PROFILE = "RASPBERRY"
        Config.SOURCE_TYPE = "VIDEO"
        Config.VIDEO_PATH = "tests/media/test_video.mp4"

    def test_plate_detection(self):
        # Crear detector
        detector = PlateDetector()
        
        # Simular detección
        with self.assertLogs('src.detector', level='INFO') as cm:
            detector.detect_plates()
        
        # Verificar logs
        self.assertIn("Iniciando detección de patentes", cm.output[0])  # <button class="citation-flag" data-index="6">
        self.assertIn("Valid plate detected: TTWC85 (Confidence: 0.97)", cm.output[1])

        self.assertIn("GPIO limpiado", cm.output[-1])  # <button class="citation-flag" data-index="6">

if __name__ == "__main__":
    unittest.main()