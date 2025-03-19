import RPi.GPIO as GPIO
import time

# Configuracin del pin GPIO
PIR_PIN = 4  # Cambia esto segn tu conexin
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Variables para filtrar falsos negativos
last_motion_time = 0
debounce_time = 2  # Tiempo mnimo entre detecciones (segundos)

try:
    print("Esperando movimiento...")
    while True:
        if GPIO.input(PIR_PIN):  # Si se detecta movimiento
            current_time = time.time()
            if current_time - last_motion_time > debounce_time:
                print("Movimiento detectado")
                last_motion_time = current_time
        else:
            print("Sin movimiento")
        time.sleep(0.5)  # Espera antes de la siguiente lectura

except KeyboardInterrupt:
    GPIO.cleanup()
