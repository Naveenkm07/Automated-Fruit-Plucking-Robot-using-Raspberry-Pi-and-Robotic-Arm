# 🤖 Automated Tomato Plucking Rover

An autonomous agricultural robot that detects and harvests ripe tomatoes using
computer vision and a servo-controlled robotic arm.

## Hardware

- **Raspberry Pi 4** (4GB RAM) — Main controller
- **Arduino UNO** — Servo/arm controller
- **PCA9685** — 16-channel servo driver (I2C)
- **SmartElex 15S** (x2) — DC motor drivers
- **DC Gear Motors** (x4) — Rover locomotion
- **MG996R Servos** (x3) — Arm joints (base, shoulder, elbow)
- **SG90 Servos** (x3) — Wrist, gripper, tilt
- **HC-SR04** (x3) — Ultrasonic obstacle detection
- **Pi Camera / USB Webcam** — Fruit detection
- **11.1V Li-ion Battery** — Power supply

## Quick Start

### 1. Copy Code to Raspberry Pi

```bash
# From your laptop (replace IP with your Pi's IP)
scp -r fruit_robot/ pi@192.168.x.x:~/
```

### 2. Install Dependencies

```bash
cd ~/fruit_robot
pip install -r requirements.txt
```

### 3. Upload Arduino Code

Open `arm/arduino_code/arm_controller.ino` in Arduino IDE and upload to Arduino UNO.

**Required Library**: Adafruit PWM Servo Driver Library
(Sketch → Include Library → Manage Libraries → Search "Adafruit PWM Servo Driver")

### 4. Test Each System

```bash
# Phase 1: Test rover motors
python3 rover/test_rover.py

# Phase 2: Test arm servos
python3 arm/test_arm.py

# Phase 3: Test serial communication
python3 arm/serial_comm.py

# Phase 4: Test camera
python3 vision/camera_test.py

# Phase 5: Test fruit detection
python3 vision/test_detection.py

# Phase 6: Test sensors
python3 sensors/ultrasonic.py
python3 sensors/light_control.py
```

### 5. Run Robot

```bash
# Manual keyboard control (recommended first)
python3 manual_control.py

# Autonomous mode
python3 main.py

# Autonomous with YOLO detection (more accurate)
python3 main.py --method yolo
```

## Project Structure

```
fruit_robot/
├── config/
│   └── pin_config.py           # GPIO pins, servo limits, settings
├── rover/
│   ├── motor_control.py        # SmartElex 15S motor driver
│   ├── rover_movement.py       # Forward, backward, turn, spin
│   └── test_rover.py           # Keyboard rover test
├── arm/
│   ├── arduino_code/
│   │   └── arm_controller.ino  # Arduino servo firmware
│   ├── serial_comm.py          # Pi ↔ Arduino communication
│   └── test_arm.py             # Interactive arm test
├── vision/
│   ├── camera_test.py          # Camera capture & preview
│   ├── fruit_detector.py       # HSV + YOLO tomato detection
│   ├── target_calculator.py    # Pixel → arm coordinate mapping
│   └── test_detection.py       # Live detection test
├── sensors/
│   ├── ultrasonic.py           # HC-SR04 distance sensors
│   └── light_control.py        # LED/relay control
├── main.py                     # Autonomous harvesting loop
├── manual_control.py           # Full keyboard control
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Configuration

All pin mappings and settings are in `config/pin_config.py`.
Edit this file to match your actual wiring.

## Manual Control Keys

| Key | Action |
|-----|--------|
| W/↑ | Forward |
| S/↓ | Backward |
| A/← | Turn Left |
| D/→ | Turn Right |
| Q/E | Spin Left/Right |
| SPACE | Emergency Stop |
| P | Pick fruit |
| O/C | Open/Close gripper |
| H | Arm home |
| L | Toggle light |
| X | Exit |

## Troubleshooting

- **Motor doesn't move**: Check common ground between Pi and SmartElex
- **Servo jitters**: Ensure external 5V power to PCA9685 V+ (not from Pi)
- **Arduino not found**: Run `ls /dev/tty* | grep -E 'ACM|USB'`
- **Camera not working**: Run `rpicam-hello` or `libcamera-hello`
- **Pi reboots**: Power supply issue — use separate regulators

## Safety

⚠️ Always test with rover wheels lifted off ground first!
⚠️ Test arm with no load before adding gripper!
⚠️ Keep emergency stop (SPACE key) ready during testing!
