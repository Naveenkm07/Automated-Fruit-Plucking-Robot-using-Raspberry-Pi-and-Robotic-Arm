import RPi.GPIO as GPIO
import time
import sys

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import (
    ULTRASONIC_TRIG_LEFT, ULTRASONIC_ECHO_LEFT,
    ULTRASONIC_TRIG_CENTER, ULTRASONIC_ECHO_CENTER,
    ULTRASONIC_TRIG_RIGHT, ULTRASONIC_ECHO_RIGHT
)

class UltrasonicSensor:
    def __init__(self, trig, echo, name):
        self.trig = trig
        self.echo = echo
        self.name = name
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, False)

    def get_distance(self):
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)
        
        pulse_start = time.time()
        timeout = pulse_start + 0.04
        while GPIO.input(self.echo) == 0 and pulse_start < timeout:
            pulse_start = time.time()
            
        pulse_end = time.time()
        timeout = pulse_end + 0.04
        while GPIO.input(self.echo) == 1 and pulse_end < timeout:
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)

class UltrasonicArray:
    def __init__(self):
        self.left = UltrasonicSensor(ULTRASONIC_TRIG_LEFT, ULTRASONIC_ECHO_LEFT, 'Left')
        self.center = UltrasonicSensor(ULTRASONIC_TRIG_CENTER, ULTRASONIC_ECHO_CENTER, 'Center')
        self.right = UltrasonicSensor(ULTRASONIC_TRIG_RIGHT, ULTRASONIC_ECHO_RIGHT, 'Right')

    def check_obstacles(self):
        left_dist = self.left.get_distance()
        center_dist = self.center.get_distance()
        right_dist = self.right.get_distance()
        
        action = 'forward'
        if center_dist < 20:
            action = 'stop'
            if left_dist > right_dist:
                action = 'turn_left'
            else:
                action = 'turn_right'
                
        return {
            'distances': {'left': left_dist, 'center': center_dist, 'right': right_dist},
            'suggested_action': action
        }
