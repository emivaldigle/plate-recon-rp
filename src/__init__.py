import logging

# Configurar logging global
logging.basicConfig(
    level=logging.DEBUG,  # Asegúrate de que el nivel sea DEBUG o inferior para capturar INFO <button class="citation-flag" data-index="2">
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("plate_recognition.log"),  # Guardar logs en un archivo <button class="citation-flag" data-index="8">
        logging.StreamHandler()  # Mostrar logs en la consola <button class="citation-flag" data-index="2">
    ]
)

logger = logging.getLogger(__name__)