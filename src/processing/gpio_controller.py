import logging
from src.config import Config
import threading
import time

class GPIOController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._blink_threads = {}  # Hilos para parpadeo <button class="citation-flag" data-index="7">
        self._stop_events = {}    # Eventos para detener parpadeos
        self.mock_gpio = False

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

    def led_on(self, led_type):
        if not self.mock_gpio:
            pin = Config.GPIO_PINS.get(led_type)
            if pin:
                # Detener parpadeo si esta activo
                if led_type in self._stop_events:
                    self.led_off(led_type)
                self.GPIO.output(pin, self.GPIO.HIGH)
                self.logger.debug(f"LED {led_type} on (pin {pin})")
        else:
            self.logger.debug(f"Mock: LED {led_type} on")

    def led_off(self, led_type):
        if not self.mock_gpio:
            pin = Config.GPIO_PINS.get(led_type)
            if pin:
                # Detener hilo de parpadeo si existe
                if led_type in self._stop_events:
                    self._stop_events[led_type].set()
                    self._blink_threads[led_type].join()
                    del self._stop_events[led_type]
                    del self._blink_threads[led_type]
                self.GPIO.output(pin, self.GPIO.LOW)
                self.logger.debug(f"LED {led_type} off")
        else:
            self.logger.debug(f"Mock: LED {led_type} off")

    def blink_led(self, led_type, interval=0.5, duration=None):
        if not self.mock_gpio:
            pin = Config.GPIO_PINS.get(led_type)
            if not pin:
                return

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
                self.GPIO.output(pin, self.GPIO.LOW)  # Asegurar apagado final <button class="citation-flag" data-index="7">

            thread = threading.Thread(target=blink, daemon=True)
            self._blink_threads[led_type] = thread
            thread.start()
            self.logger.debug(f"LED {led_type} blinking started")
        else:
            self.logger.debug(f"Mock: LED {led_type} blinking")

    def cleanup(self):
        if not self.mock_gpio:
            # Detener todos los parpadeos activos
            for led_type in list(self._stop_events.keys()):
                self.led_off(led_type)
            self.GPIO.cleanup()
            self.logger.info("GPIO cleaned")
        else:
            self.logger.info("Mock: GPIO cleaned")
