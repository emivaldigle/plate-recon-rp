import logging
import logging.handlers
import queue  # Para usar QueueHandler

# Crear una cola para los logs
log_queue = queue.Queue()

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.handlers.QueueHandler(log_queue),  # Usando la cola para el QueueHandler
        logging.FileHandler("/plate_recognition.log", mode='a'),
    ]
)

logger = logging.getLogger(__name__)
