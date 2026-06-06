# sensors/obstacle_sensors.py
#
# Handles ALL 6 obstacle sensors:
#
#   HC-SR04 Ultrasonic (3 sensors):
#       Front  — center front bumper
#       Left   — left side
#       Right  — right side
#
#   IR Proximity Sensors (3 sensors):
#       Front-Left  — front-left corner
#       Front-Right — front-right corner
#       Back        — center back
#
# The rover uses these readings to avoid obstacles
# and decide which direction is safe to move.

import RPi.GPIO as GPIO
import time
import sys

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import (
    US_FRONT_TRIG, US_FRONT_ECHO,
    US_LEFT_TRIG,  US_LEFT_ECHO,
    US_RIGHT_TRIG, US_RIGHT_ECHO,
    IR_FRONT_LEFT_PIN, IR_FRONT_RIGHT_PIN, IR_BACK_PIN,
    US_STOP_DISTANCE_CM
)


# ─────────────────────────────────────────────────
# HC-SR04 Ultrasonic Sensor
# ─────────────────────────────────────────────────
class UltrasonicSensor:
    """
    Single HC-SR04 ultrasonic sensor.
    Returns distance in cm.

    ⚠️  Echo pin MUST go through voltage divider before Pi!
        Trig pin connects directly to Pi.
    """

    def __init__(self, trig_pin, echo_pin, name='US'):
        self.trig = trig_pin
        self.echo = echo_pin
        self.name = name

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, False)
        time.sleep(0.05)   # let sensor settle

    def get_distance(self):
        """
        Fire a trigger pulse and measure echo time.
        Returns distance in cm. Returns 999 if nothing detected / timeout.
        """
        # Send 10µs trigger pulse
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        # Wait for echo to go HIGH (with timeout)
        pulse_start = time.time()
        timeout = pulse_start + 0.04
        while GPIO.input(self.echo) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return 999   # no echo received

        # Wait for echo to go LOW (with timeout)
        pulse_end = time.time()
        timeout = pulse_end + 0.04
        while GPIO.input(self.echo) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return 999   # echo too long (object too far)

        # Calculate distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150   # (34300 cm/s) / 2
        return round(distance, 1)

    def is_obstacle(self, threshold_cm=None):
        """
        Returns (True, distance) if obstacle is within threshold,
                (False, distance) if clear.
        """
        threshold_cm = threshold_cm or US_STOP_DISTANCE_CM
        dist = self.get_distance()
        return dist < threshold_cm, dist


# ─────────────────────────────────────────────────
# IR Proximity / Photoelectric Sensor
# ─────────────────────────────────────────────────
class IRSensor:
    """
    Single IR proximity / photoelectric sensor.

    OUT pin logic:
        HIGH (1) = No obstacle (clear)
        LOW  (0) = Obstacle detected!

    OUT pin is 3.3V logic → connects directly to Pi ✅
    """

    def __init__(self, pin, name='IR'):
        self.pin = pin
        self.name = name

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Pull-up: default HIGH (clear), goes LOW when obstacle detected
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_obstacle(self):
        """Returns True if an obstacle is detected (OUT pin is LOW)."""
        return GPIO.input(self.pin) == GPIO.LOW


# ─────────────────────────────────────────────────
# Combined Obstacle Sensor Array (all 6 sensors)
# ─────────────────────────────────────────────────
class ObstacleSensorArray:
    """
    Manages all 6 sensors and decides which direction is safe.

    Layout:
        [IR Front-Left]  [US Front]  [IR Front-Right]
        [US Left]       (ROBOT)      [US Right]
                        [IR Back]
    """

    def __init__(self):
        print('[SENSORS] Initializing all 6 obstacle sensors...')

        # Ultrasonic sensors
        self.us_front = UltrasonicSensor(US_FRONT_TRIG, US_FRONT_ECHO, 'US-Front')
        self.us_left  = UltrasonicSensor(US_LEFT_TRIG,  US_LEFT_ECHO,  'US-Left')
        self.us_right = UltrasonicSensor(US_RIGHT_TRIG, US_RIGHT_ECHO, 'US-Right')

        # IR sensors
        self.ir_front_left  = IRSensor(IR_FRONT_LEFT_PIN,  'IR-FrontLeft')
        self.ir_front_right = IRSensor(IR_FRONT_RIGHT_PIN, 'IR-FrontRight')
        self.ir_back        = IRSensor(IR_BACK_PIN,         'IR-Back')

        print('[SENSORS] ✅ All 6 sensors initialized!')
        print()
        print('  Ultrasonic:')
        print(f'    Front  → TRIG GPIO {US_FRONT_TRIG} (Pin 15)  /  ECHO GPIO {US_FRONT_ECHO} (Pin 16)')
        print(f'    Left   → TRIG GPIO {US_LEFT_TRIG}  (Pin 18)  /  ECHO GPIO {US_LEFT_ECHO}  (Pin 22)')
        print(f'    Right  → TRIG GPIO {US_RIGHT_TRIG} (Pin 36)  /  ECHO GPIO {US_RIGHT_ECHO} (Pin 37)')
        print()
        print('  IR Sensors:')
        print(f'    Front-Left  → GPIO {IR_FRONT_LEFT_PIN}  (Pin 11)')
        print(f'    Front-Right → GPIO {IR_FRONT_RIGHT_PIN} (Pin 13)')
        print(f'    Back        → GPIO {IR_BACK_PIN}         (Pin 7)')
        print()

    def read_all(self):
        """
        Read all 6 sensors and return a full status dictionary.

        Returns:
        {
            'front_dist':        35.2,     # cm (999 = nothing)
            'left_dist':         80.0,
            'right_dist':        999,
            'front_clear':       True,     # US front OK
            'left_clear':        True,     # US left OK
            'right_clear':       True,     # US right OK
            'ir_front_left':     False,    # True = obstacle
            'ir_front_right':    False,
            'ir_back':           False,
            'front_ok':          True,     # combined: safe to go forward
            'back_ok':           True,     # safe to reverse
            'action':            'forward' # recommended rover action
        }
        """
        # Read ultrasonic
        front_blocked, front_dist = self.us_front.is_obstacle()
        left_blocked,  left_dist  = self.us_left.is_obstacle()
        right_blocked, right_dist = self.us_right.is_obstacle()

        # Read IR
        ir_fl = self.ir_front_left.is_obstacle()
        ir_fr = self.ir_front_right.is_obstacle()
        ir_bk = self.ir_back.is_obstacle()

        # Front is safe only if US front is clear AND both front IR sensors are clear
        front_ok = (not front_blocked) and (not ir_fl) and (not ir_fr)
        # Back is safe only if back IR is clear
        back_ok  = not ir_bk
        # Left/Right based on US sensors
        left_ok  = not left_blocked
        right_ok = not right_blocked

        # Decide recommended action
        if front_ok:
            action = 'forward'
        elif left_ok and not right_ok:
            action = 'spin_left'
        elif right_ok and not left_ok:
            action = 'spin_right'
        elif left_ok and right_ok:
            # Both sides free — turn slightly left to search
            action = 'spin_left'
        elif back_ok:
            action = 'backward'
        else:
            action = 'stop'

        return {
            'front_dist':       front_dist,
            'left_dist':        left_dist,
            'right_dist':       right_dist,
            'front_blocked':    front_blocked,
            'left_blocked':     left_blocked,
            'right_blocked':    right_blocked,
            'ir_front_left':    ir_fl,
            'ir_front_right':   ir_fr,
            'ir_back':          ir_bk,
            'front_ok':         front_ok,
            'back_ok':          back_ok,
            'left_ok':          left_ok,
            'right_ok':         right_ok,
            'action':           action
        }

    def is_safe_to_move(self, direction='forward'):
        """Quick single-direction safety check."""
        data = self.read_all()
        mapping = {
            'forward':  data['front_ok'],
            'backward': data['back_ok'],
            'left':     data['left_ok'],
            'right':    data['right_ok'],
        }
        return mapping.get(direction, True)

    def cleanup(self):
        GPIO.cleanup()
        print('[SENSORS] GPIO cleaned up.')


# ─────────────────────────────────────────────────
# STANDALONE TEST — run directly to verify wiring
# ─────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 55)
    print('  OBSTACLE SENSOR TEST')
    print('  Hold something in front of each sensor to test')
    print('  Press Ctrl+C to stop')
    print('=' * 55)

    sensors = None
    try:
        sensors = ObstacleSensorArray()

        while True:
            d = sensors.read_all()

            print(f"\n  ── Ultrasonic ──────────────────────────────")
            print(f"  Front : {d['front_dist']:6.1f} cm  {'🔴 BLOCKED' if d['front_blocked'] else '🟢 clear'}")
            print(f"  Left  : {d['left_dist']:6.1f} cm  {'🔴 BLOCKED' if d['left_blocked']  else '🟢 clear'}")
            print(f"  Right : {d['right_dist']:6.1f} cm  {'🔴 BLOCKED' if d['right_blocked'] else '🟢 clear'}")
            print(f"\n  ── IR Sensors ──────────────────────────────")
            print(f"  Front-Left  : {'🔴 OBSTACLE' if d['ir_front_left']  else '🟢 clear'}")
            print(f"  Front-Right : {'🔴 OBSTACLE' if d['ir_front_right'] else '🟢 clear'}")
            print(f"  Back        : {'🔴 OBSTACLE' if d['ir_back']        else '🟢 clear'}")
            print(f"\n  ── Recommended Action ─────────────────────")
            print(f"  ➡  {d['action'].upper()}")
            print('  ' + '─' * 45)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print('\n[TEST] Stopped by user.')
    finally:
        if sensors:
            sensors.cleanup()
