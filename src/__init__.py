import logging
import logging.handlers

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.handlers.QueueHandler(logging.handlers.Queue()),
        logging.FileHandler("/plate_recognition.log", mode='a'),
    ]
)

logger = logging.getLogger(__name__)
