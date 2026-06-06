import RPi.GPIO as GPIO
import time
import sys
import threading

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import RELAY_LED_LIGHT, RELAY_WATER_PUMP

class LightController:
    def __init__(self, active_low=True):
        self.active_low = active_low
        self.led_pin = RELAY_LED_LIGHT
        self.pump_pin = RELAY_WATER_PUMP
        self.led_is_on = False
        self.pump_is_on = False
        self._pump_timer = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.pump_pin, GPIO.OUT)

        self._set_relay(self.led_pin, False)
        self._set_relay(self.pump_pin, False)

    def _set_relay(self, pin, on):
        if self.active_low:
            GPIO.output(pin, GPIO.LOW if on else GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.HIGH if on else GPIO.LOW)

    def turn_on_led(self):
        self._set_relay(self.led_pin, True)
        self.led_is_on = True

    def turn_off_led(self):
        self._set_relay(self.led_pin, False)
        self.led_is_on = False

    def toggle_led(self):
        if self.led_is_on:
            self.turn_off_led()
        else:
            self.turn_on_led()

    def turn_on_pump(self, duration=None):
        self._set_relay(self.pump_pin, True)
        self.pump_is_on = True
        if duration:
            if self._pump_timer:
                self._pump_timer.cancel()
            self._pump_timer = threading.Timer(duration, self.turn_off_pump)
            self._pump_timer.start()

    def turn_off_pump(self):
        self._set_relay(self.pump_pin, False)
        self.pump_is_on = False
        if self._pump_timer:
            self._pump_timer.cancel()
            self._pump_timer = None

    def cleanup(self):
        self.turn_off_led()
        self.turn_off_pump()
