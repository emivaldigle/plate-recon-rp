import unittest
from src.processing.detector import PlateDetector
from src.config import Config

class TestPlateDetectionUbuntu(unittest.TestCase):
    def setUp(self):
        # Configurar perfil UBUNTU
        Config.PROFILE = "UBUNTU"
        Config.SOURCE_TYPE = "VIDEO"
        Config.VIDEO_PATH = "tests/media/test_video.mp4"

    def test_plate_detection(self):
        # Crear detector
        detector = PlateDetector()
        
        # Simular detección con un máximo de 10 frames
        with self.assertLogs('src.detector', level='INFO') as cm:  # Coincidir con el nombre "detector" <button class="citation-flag" data-index="2">
            detector.detect_plates(max_frames=10)
        
        # Verificar logs
        self.assertIn("Starting plate detection...", cm.output[0])  # <button class="citation-flag" data-index="7">
        self.assertIn("Valid plate detected: TTWC85 (Confidence: 0.97)", cm.output[1])
        self.assertIn("Processing stopped after frame number ", cm.output[-1])  # <button class="citation-flag" data-index="7">

if __name__ == "__main__":
    unittest.main()