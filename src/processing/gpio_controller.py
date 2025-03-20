import logging
from src.config import Config
import threading
import time

class GPIOController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._blink_threads = {}  # Hilos para parpadeo
        self._stop_events = {}    # Eventos para detener parpadeos
        self.mock_gpio = False
        self._mock_states = {}    # Estados simulados de los pines
        self.motion_detected = False  # Estado del sensor de movimiento

        # Verificar entorno Raspberry Pi
        if Config.PROFILE == "RASPBERRY":
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.GPIO.setmode(self.GPIO.BCM)
                for pin in Config.GPIO_PINS.values():
                    self.GPIO.setup(pin, self.GPIO.OUT)
                    self.GPIO.output(pin, self.GPIO.LOW)
                self.logger.info("GPIO initialized successfully")
            except ImportError:
                self.mock_gpio = True
                self.logger.warning("Using mock GPIO (RPi.GPIO not found)")
        else:
            self.mock_gpio = True
            self.logger.warning("Mocked GPIO (profile: UBUNTU)")

        # Inicializar estados simulados
        if self.mock_gpio:
            for led_type, pin in Config.GPIO_PINS.items():
                self._mock_states[pin] = False  # Todos los LEDs comienzan apagados

        # Configurar el pin del sensor de movimiento
        
        self.MOTION_SENSOR_PIN = Config.GPIO_PINS.get("motion_sensor")
        if not self.MOTION_SENSOR_PIN:
            raise ValueError("Motion sensor pin is not configured in GPIO_PINS.")
        if not self.mock_gpio:
            self.GPIO.setup(self.MOTION_SENSOR_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)

    def led_on(self, led_type):
        pin = Config.GPIO_PINS.get(led_type)
        if not pin:
            self.logger.error(f"Invalid LED type: {led_type}")
            return

        if not self.mock_gpio:
            # Detener parpadeo si está activo
            if led_type in self._stop_events:
                self.led_off(led_type)
            self.GPIO.output(pin, self.GPIO.HIGH)
            self.logger.debug(f"LED {led_type} on (pin {pin})")
        else:
            # Simular encendido
            self._mock_states[pin] = True
            self.logger.debug(f"Mock: LED {led_type} on (pin {pin})")


    def led_off(self, led_type):
        pin = Config.GPIO_PINS.get(led_type)
        if not pin:
            self.logger.error(f"Invalid LED type: {led_type}")
            return

        if not self.mock_gpio:
            # Detener hilo de parpadeo si existe
            if led_type in self._stop_events:
                self._stop_events[led_type].set()  # Signal para detener el hilo
                self._blink_threads[led_type].join(timeout=1)  # Esperar a que termine
                del self._stop_events[led_type]
                del self._blink_threads[led_type]

            # Apagar LED asegurando que la senal sea LOW
            self.GPIO.output(pin, self.GPIO.LOW)
            self.logger.debug(f"LED {led_type} off (pin {pin})")
        else:
            self._mock_states[pin] = False
            self.logger.debug(f"Mock: LED {led_type} off (pin {pin})")
        
        # Verificar que el LED realmente esta en LOW
        if not self.mock_gpio:
            actual_state = self.GPIO.input(pin)
            self.logger.debug(f"LED {led_type} state after off: {actual_state}")


    def cleanup(self):
        if not self.mock_gpio:
            # Detener todos los parpadeos activos
            for led_type in list(self._stop_events.keys()):
                self.led_off(led_type)
            self.GPIO.cleanup()
            self.logger.info("GPIO cleaned")
        else:
            # Limpiar estados simulados
            for pin in self._mock_states:
                self._mock_states[pin] = False
            self.logger.info("Mock: GPIO cleaned")

    def monitor_motion_sensor(self, callback=None):
        if not self.mock_gpio:
            try:
                self.logger.info("Starting motion sensor monitoring...")
                last_state = self.GPIO.input(self.MOTION_SENSOR_PIN)  # Estado inicial

                while True:
                    motion_detected = self.GPIO.input(self.MOTION_SENSOR_PIN)

                    if motion_detected != last_state:  # Solo imprimir si el estado cambia
                        last_state = motion_detected
                        self.logger.debug("Motion detected!" if motion_detected else "Motion stopped.")

                        if motion_detected and callback:
                            try:
                                callback()
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")

                    time.sleep(0.1)  # Reducir el tiempo de espera
            except KeyboardInterrupt:
                self.logger.info("Stopping motion sensor monitoring.")
