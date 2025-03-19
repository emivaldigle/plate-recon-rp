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
            self.GPIO.setup(self.MOTION_SENSOR_PIN, self.GPIO.IN)

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
                self._stop_events[led_type].set()
                self._blink_threads[led_type].join()
                del self._stop_events[led_type]
                del self._blink_threads[led_type]
            self.GPIO.output(pin, self.GPIO.LOW)
            self.logger.debug(f"LED {led_type} off")
        else:
            # Simular apagado
            self._mock_states[pin] = False
            self.logger.debug(f"Mock: LED {led_type} off (pin {pin})")

    def blink_led(self, led_type, interval=0.5, duration=None):
        pin = Config.GPIO_PINS.get(led_type)
        if not pin:
            self.logger.error(f"Invalid LED type: {led_type}")
            return

        if not self.mock_gpio:
            # Crear evento y hilo para el parpadeo
            stop_event = threading.Event()
            self._stop_events[led_type] = stop_event

            def blink():
                start_time = time.time()
                while (duration is None or time.time() - start_time < duration) and not stop_event.is_set():
                    self.GPIO.output(pin, self.GPIO.HIGH)
                    stop_event.wait(interval)
                    self.GPIO.output(pin, self.GPIO.LOW)
                    stop_event.wait(interval)
                self.GPIO.output(pin, self.GPIO.LOW)  # Asegurar apagado final

            thread = threading.Thread(target=blink, daemon=True)
            self._blink_threads[led_type] = thread
            thread.start()
            self.logger.debug(f"LED {led_type} blinking started")
        else:
            # Simular parpadeo
            def mock_blink():
                start_time = time.time()
                while (duration is None or time.time() - start_time < duration):
                    self._mock_states[pin] = True
                    self.logger.debug(f"Mock: LED {led_type} blinking HIGH (pin {pin})")
                    time.sleep(interval)
                    self._mock_states[pin] = False
                    self.logger.debug(f"Mock: LED {led_type} blinking LOW (pin {pin})")
                    time.sleep(interval)

            stop_event = threading.Event()
            self._stop_events[led_type] = stop_event

            def mock_blink_wrapper():
                mock_blink()
                self._mock_states[pin] = False  # Asegurar apagado final

            thread = threading.Thread(target=mock_blink_wrapper, daemon=True)
            self._blink_threads[led_type] = thread
            thread.start()
            self.logger.debug(f"Mock: LED {led_type} blinking started")

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
                while True:
                    motion_detected = self.GPIO.input(self.MOTION_SENSOR_PIN)
                    if motion_detected and not self.motion_detected:
                        self.logger.debug("Motion detected!")
                        self.motion_detected = True
                        if callback:
                            callback()
                    elif not motion_detected and self.motion_detected:
                        self.logger.debug("Motion stopped.")
                        self.motion_detected = False
                    time.sleep(0.1)  # Pequeña pausa para evitar lecturas rápidas
            except KeyboardInterrupt:
                self.logger.info("Stopping motion sensor monitoring.")
        else:
            # Simulación del sensor de movimiento
            try:
                while True:
                    # Simular detección de movimiento cada 5 segundos
                    time.sleep(5)
                    self.logger.debug("Mock: Motion detected!")
                    self.motion_detected = True
                    if callback:
                        callback()
                    time.sleep(5)
                    self.logger.debug("Mock: Motion stopped.")
                    self.motion_detected = False
            except KeyboardInterrupt:
                self.logger.info("Stopping mock motion sensor monitoring.")
