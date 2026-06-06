import sys
import time

try:
    import tty
    import termios
except ImportError:
    print("WARNING: tty/termios modules not found. This script must be run on Linux/Raspberry Pi.")
    sys.exit(1)

sys.path.insert(0, '/home/fruit/fruit_robot')
from rover.rover_movement import RoverController

def get_char():
    """Reads a single character from the keyboard without needing to press Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  🎮 MANUAL ROVER CONTROL")
    print("  Use W / A / S / D to move.")
    print("  Press SPACE to stop the motors.")
    print("  Press 'Q' to quit.")
    print("="*50 + "\n")
    
    rover = None
    try:
        rover = RoverController()
        print("Ready for input!")
        
        while True:
            char = get_char().lower()
            
            if char == 'w':
                rover.forward()
            elif char == 's':
                rover.backward()
            elif char == 'a':
                rover.turn_left()
            elif char == 'd':
                rover.turn_right()
            elif char == ' ':
                rover.stop()
            elif char == 'q':
                break
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if rover:
            rover.cleanup()
        print("\nExited manual control.")
