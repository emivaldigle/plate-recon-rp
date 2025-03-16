import logging

# Configurar logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("plate_recognition.log"),
        logging.StreamHandler()]
)

logger = logging.getLogger(__name__)