import logging
from src.config import Config

class GPIOController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if Config.PROFILE == "RASPBERRY":
            try:
                import RPi.GPIO as GPIO  # Intentar importar GPIO real <button class="citation-flag" data-index="6">
                self.GPIO = GPIO
                self.mock_gpio = False
                self.logger.info("GPIO succesfully started")
            except ImportError:
                self.mock_gpio = True
                self.logger.warning("Unable to import RPi.GPIO using mock instead")  # Mock por defecto <button class="citation-flag" data-index="7">
        else:
            self.mock_gpio = True
            self.logger.warning("mocked GPIO (profile: UBUNTU)")  # Mock para Ubuntu <button class="citation-flag" data-index="7">

        if not self.mock_gpio:
            self.GPIO.setmode(self.GPIO.BCM)
            for pin in Config.GPIO_PINS.values():
                self.GPIO.setup(pin, self.GPIO.OUT)
                self.GPIO.output(pin, self.GPIO.LOW)

    def led_on(self, led_type):
        if not self.mock_gpio:
            pin = Config.GPIO_PINS.get(led_type)
            if pin:
                self.GPIO.output(pin, self.GPIO.HIGH)
                self.logger.debug(f"LED {led_type} on (pin {pin})")
        else:
            self.logger.debug(f"Mock: LED {led_type} on")  # <button class="citation-flag" data-index="7">

    def led_off(self, led_type):
        if not self.mock_gpio:
            pin = Config.GPIO_PINS.get(led_type)
            if pin:
                self.GPIO.output(pin, self.GPIO.LOW)
        else:
            self.logger.debug(f"Mock: LED {led_type} off")  # <button class="citation-flag" data-index="7">

    def cleanup(self):
        if not self.mock_gpio:
            self.GPIO.cleanup()
            self.logger.info("GPIO cleaned")
        else:
            self.logger.info("Mock: GPIO cleaned")  # <button class="citation-flag" data-index="7">