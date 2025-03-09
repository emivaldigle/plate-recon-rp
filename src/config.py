import logging

class Config:
    # Perfil actual (cambiar según el entorno)
    PROFILE = "RASPBERRY"  # Opciones: "UBUNTU" o "RASPBERRY" <button class="citation-flag" data-index="7">

    # Configuración general
    SOURCE_TYPE = "STREAM"
    VIDEO_PATH = "tests/media/test_video.mp4"
    STREAM_URL = "http://localhost:8080/stream"

    # Thresholds
    DETECTION_CONFIDENCE = 0.7
    OCR_CONFIDENCE = 0.85

    # HTTP Server
    HTTP_SERVER_HOST = "http://mock-server:8000"

    # Logging
    LOGGING_LEVEL = logging.DEBUG
    LOG_FILE = "plate_recognition.log"

    # GPIO Pins (solo para Raspberry Pi)
    if PROFILE == "RASPBERRY":
        GPIO_PINS = {
            "processing": 18,   # Azul
            "access_granted": 23,  # Verde
            "access_denied": 24    # Rojo <button class="citation-flag" data-index="6">
        }
    else:
        GPIO_PINS = {}  # Desactivar GPIO en Ubuntu <button class="citation-flag" data-index="7">