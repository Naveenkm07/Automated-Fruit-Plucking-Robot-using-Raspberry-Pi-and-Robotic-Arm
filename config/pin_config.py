# config/pin_config.py

# ─────────────────────────────────────────
# MOTOR PINS (SmartElex 15S)
# ─────────────────────────────────────────
LEFT_MOTOR_PWM = 12   # Physical Pin 32
LEFT_MOTOR_DIR = 5    # Physical Pin 29
RIGHT_MOTOR_PWM = 13  # Physical Pin 33
RIGHT_MOTOR_DIR = 6   # Physical Pin 31
MOTOR_DEFAULT_SPEED = 60

# ─────────────────────────────────────────
# ARM / ARDUINO
# ─────────────────────────────────────────
ARM_SERIAL_PORT = '/dev/ttyUSB0'
ARM_BAUD_RATE = 115200

# ─────────────────────────────────────────
# CAMERA
# ─────────────────────────────────────────
CAMERA_TYPE = 'picamera'       # 'picamera' or 'usb'
CAMERA_USB_INDEX = 0
CAMERA_RESOLUTION = (640, 480)

# ─────────────────────────────────────────
# FRUIT DETECTION (HSV Color Ranges)
# ─────────────────────────────────────────
HSV_LOWER_RED1 = [0, 120, 70]
HSV_UPPER_RED1 = [10, 255, 255]
HSV_LOWER_RED2 = [170, 120, 70]
HSV_UPPER_RED2 = [180, 255, 255]
MIN_FRUIT_AREA = 500
DETECTION_CONFIDENCE = 0.5

# ─────────────────────────────────────────
# HC-SR04 ULTRASONIC SENSORS (3 sensors)
#
# Sensor layout:
#          [US FRONT]
#  [US LEFT]  ROBOT  [US RIGHT]
#
# ⚠️  ECHO pin outputs 5V — DANGEROUS for Pi!
#     Use voltage divider on EVERY Echo wire:
#     Echo → 1kΩ → Pi GPIO
#                ↘ 2kΩ → GND
#
# TRIG pins connect directly to Pi (3.3V OK ✅)
# ─────────────────────────────────────────
US_FRONT_TRIG = 22   # Physical Pin 15
US_FRONT_ECHO = 23   # Physical Pin 16  ⚠️ via voltage divider

US_LEFT_TRIG  = 24   # Physical Pin 18
US_LEFT_ECHO  = 25   # Physical Pin 22  ⚠️ via voltage divider

US_RIGHT_TRIG = 16   # Physical Pin 36
US_RIGHT_ECHO = 26   # Physical Pin 37  ⚠️ via voltage divider

# Distance threshold — rover stops/avoids if closer than this
US_STOP_DISTANCE_CM = 25

# ─────────────────────────────────────────
# IR PROXIMITY / PHOTOELECTRIC SENSORS (3)
#
# Sensor layout:
#  [IR FL] [US FRONT] [IR FR]   ← Front side
#
#          [IR BACK]            ← Back side
#
# IR OUT pin = 3.3V logic → connects DIRECTLY to Pi ✅
# HIGH = No obstacle   /   LOW = Obstacle detected
# ─────────────────────────────────────────
IR_FRONT_LEFT_PIN  = 17   # Physical Pin 11
IR_FRONT_RIGHT_PIN = 27   # Physical Pin 13
IR_BACK_PIN        = 4    # Physical Pin 7

# ─────────────────────────────────────────
# RELAY OUTPUTS
# ─────────────────────────────────────────
RELAY_LED_LIGHT  = 20   # Physical Pin 38
RELAY_WATER_PUMP = 21   # Physical Pin 40

# ─────────────────────────────────────────
# SERVO LIMITS (Robotic Arm)
# ─────────────────────────────────────────
SERVO_LIMITS = {
    0: (0, 180),
    1: (45, 135),
    2: (45, 135),
    3: (0, 180),
    4: (30, 110),   # Gripper
    5: (0, 180)
}
