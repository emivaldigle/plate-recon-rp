import logging
from dotenv import load_dotenv
load_dotenv(verbose=True, override=True)
import os
 # Carga automáticamente las variables desde .env
class Config:
    # Perfil actual (cambiar según el entorno)
    PROFILE = os.getenv("PROFILE", "RASPBERRY")  # Opciones: "UBUNTU" o "RASPBERRY" <button class="citation-flag" data-index="7">

    # Configuración general
    SOURCE_TYPE = os.getenv("SOURCE_TYPE", "CAMERA")  # Default a "VIDEO"
    VIDEO_PATH = os.getenv("VIDEO_PATH")
    STREAM_URL = os.getenv("STREAM_URL")

    # Ocr
    os.environ["QT_QPA_PLATFORM"] = "vnc" # vnc for raspberry and xcb for ubuntu
    os.environ["DISPLAY"] = "0" # 0 for vnc
    # Thresholds
    DETECTION_CONFIDENCE = 0.89
    OCR_CONFIDENCE = 0.95

    # Local database
    DATABASE_URL = "gate_command_local.db"
    ENTITY_ID = os.getenv("ENTITY_ID")
    POC_ID = os.getenv("POC_ID")

    # HTTP Server
    HTTP_SERVER_HOST = os.getenv("HTTP_SERVER_HOST")
    # MQTT Server
    MQTT_SERVER_HOST = os.getenv("MQTT_SERVER_HOST")
    MQTT_SERVER_PORT = os.getenv("MQTT_SERVER_PORT", 1883)

    # Logging
    LOGGING_LEVEL = logging.DEBUG
    LOG_FILE = "plate_recognition.log"

    # GPIO Pins (solo para Raspberry Pi)
    if PROFILE == "RASPBERRY":
        GPIO_PINS = {
            "processing": 18,   # Azul
            "access_granted": 23,  # Verde
            "access_denied": 24, # Rojo
            "motion_sensor": 17    # Motion
        }
    else:
        GPIO_PINS = {} 

    print(f"SOURCE_TYPE: {SOURCE_TYPE}")
    print(f"VIDEO_PATH: {VIDEO_PATH}")
    print(f"STREAM_URL: {STREAM_URL}")
