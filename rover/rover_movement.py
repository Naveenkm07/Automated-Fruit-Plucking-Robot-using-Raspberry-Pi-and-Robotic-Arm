import RPi.GPIO as GPIO
import time
import sys

sys.path.insert(0, '/home/fruit/fruit_robot')
from config.pin_config import (
    LEFT_MOTOR_PWM, LEFT_MOTOR_DIR,
    RIGHT_MOTOR_PWM, RIGHT_MOTOR_DIR,
    MOTOR_DEFAULT_SPEED
)
from rover.motor_control import MotorDriver


class RoverController:
    """
    High-level rover movement controller.
    Controls both left and right motor drivers for differential steering.
    """

    def __init__(self):
        """Initialize both motor drivers."""
        print("=" * 50)
        print("  ROVER CONTROLLER — Initializing")
        print("=" * 50)

        self.left_motor = MotorDriver(LEFT_MOTOR_PWM, LEFT_MOTOR_DIR, "Left")
        self.right_motor = MotorDriver(RIGHT_MOTOR_PWM, RIGHT_MOTOR_DIR, "Right")
        self.is_moving = False

        print("[ROVER] ✅ Both motors initialized successfully!\n")

    def forward(self, speed=None):
        speed = speed or MOTOR_DEFAULT_SPEED
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)
        self.is_moving = True
        print(f"[ROVER] ➡ FORWARD at {speed}%")

    def backward(self, speed=None):
        speed = speed or MOTOR_DEFAULT_SPEED
        self.left_motor.reverse(speed)
        self.right_motor.reverse(speed)
        self.is_moving = True
        print(f"[ROVER] ⬅ BACKWARD at {speed}%")

    def turn_left(self, speed=None):
        speed = speed or MOTOR_DEFAULT_SPEED
        self.left_motor.forward(int(speed * 0.3))  
        self.right_motor.forward(speed)              
        self.is_moving = True
        print(f"[ROVER] ↰ TURN LEFT at {speed}%")

    def turn_right(self, speed=None):
        speed = speed or MOTOR_DEFAULT_SPEED
        self.left_motor.forward(speed)               
        self.right_motor.forward(int(speed * 0.3))   
        self.is_moving = True
        print(f"[ROVER] ↱ TURN RIGHT at {speed}%")

    def spin_left(self, speed=None):
        speed = speed or int(MOTOR_DEFAULT_SPEED * 0.6)
        self.left_motor.reverse(speed)
        self.right_motor.forward(speed)
        self.is_moving = True
        print(f"[ROVER] ⟲ SPIN LEFT at {speed}%")

    def spin_right(self, speed=None):
        speed = speed or int(MOTOR_DEFAULT_SPEED * 0.6)
        self.left_motor.forward(speed)
        self.right_motor.reverse(speed)
        self.is_moving = True
        print(f"[ROVER] ⟳ SPIN RIGHT at {speed}%")

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
        self.is_moving = False
        print("[ROVER] ⏹ STOPPED")

    def brake(self):
        self.left_motor.brake()
        self.right_motor.brake()
        self.is_moving = False
        print("[ROVER] 🛑 BRAKE applied")

    def smooth_forward(self, target_speed=None, duration=1.5):
        target_speed = target_speed or MOTOR_DEFAULT_SPEED
        self.left_motor.forward(0)
        self.right_motor.forward(0)
        self.left_motor.smooth_accelerate(target_speed, duration)
        self.right_motor.smooth_accelerate(target_speed, duration)
        self.is_moving = True
        print(f"[ROVER] ➡ Smooth forward to {target_speed}%")

    def move_for_duration(self, direction, speed, duration):
        commands = {
            'forward': self.forward,
            'backward': self.backward,
            'left': self.turn_left,
            'right': self.turn_right,
            'spin_left': self.spin_left,
            'spin_right': self.spin_right,
        }

        if direction in commands:
            commands[direction](speed)
            time.sleep(duration)
            self.stop()
        else:
            print(f"[ROVER] ❌ Unknown direction: {direction}")

    def set_differential_speed(self, left_speed, right_speed, left_dir='forward', right_dir='forward'):
        if left_dir == 'forward':
            self.left_motor.forward(left_speed)
        else:
            self.left_motor.reverse(left_speed)

        if right_dir == 'forward':
            self.right_motor.forward(right_speed)
        else:
            self.right_motor.reverse(right_speed)

        self.is_moving = True

    def cleanup(self):
        self.stop()
        self.left_motor.cleanup()
        self.right_motor.cleanup()
        print("[ROVER] ✅ Cleanup complete")


if __name__ == "__main__":
    print("=" * 50)
    print("  ROVER MOVEMENT TEST")
    print("  Testing all movement directions")
    print("=" * 50)

    rover = None
    try:
        rover = RoverController()

        print("\n--- Forward 3 sec ---")
        rover.forward(50)
        time.sleep(3)
        rover.stop()
        time.sleep(1)

        print("\n--- Backward 3 sec ---")
        rover.backward(50)
        time.sleep(3)
        rover.stop()
        time.sleep(1)

        print("\n--- Turn Left 2 sec ---")
        rover.turn_left(50)
        time.sleep(2)
        rover.stop()
        time.sleep(1)

        print("\n--- Turn Right 2 sec ---")
        rover.turn_right(50)
        time.sleep(2)
        rover.stop()
        time.sleep(1)

        print("\n--- Spin Left 2 sec ---")
        rover.spin_left(40)
        time.sleep(2)
        rover.stop()
        time.sleep(1)

        print("\n--- Spin Right 2 sec ---")
        rover.spin_right(40)
        time.sleep(2)
        rover.stop()

        print("\n✅ All movement tests PASSED!")

    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
    finally:
        if rover:
            rover.cleanup()
        GPIO.cleanup()
