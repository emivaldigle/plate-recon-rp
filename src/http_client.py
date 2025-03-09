import requests
import logging
from src.config import Config

class HttpClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_plate(self, plate_text):
        try:
            response = requests.post(
                f"{Config.HTTP_SERVER_HOST}/api/plates",
                json={"plate": plate_text}
            )
            self.logger.info(f"HTTP Request: {plate_text} | Response: {response.status_code}")  # <button class="citation-flag" data-index="2">
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error en HTTP request: {str(e)}")
            return False