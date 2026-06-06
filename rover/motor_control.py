import RPi.GPIO as GPIO
import time

class MotorDriver:
    def __init__(self, pwm_pin, dir_pin, name='Motor'):
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin
        self.name = name
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.pwm_pin, 1000)
        self.pwm.start(0)

    def forward(self, speed):
        GPIO.output(self.dir_pin, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)

    def reverse(self, speed):
        GPIO.output(self.dir_pin, GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)

    def stop(self):
        self.pwm.ChangeDutyCycle(0)

    def brake(self):
        GPIO.output(self.dir_pin, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)

    def smooth_accelerate(self, target_speed, duration=1.0):
        GPIO.output(self.dir_pin, GPIO.HIGH)
        steps = 10
        for i in range(1, steps + 1):
            speed = (target_speed / steps) * i
            self.pwm.ChangeDutyCycle(speed)
            time.sleep(duration / steps)

    def cleanup(self):
        self.stop()
        self.pwm.stop()
