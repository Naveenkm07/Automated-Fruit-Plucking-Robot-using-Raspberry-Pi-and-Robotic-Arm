import sys
import time

sys.path.insert(0, '/home/fruit/fruit_robot')
from rover.rover_movement import RoverController

if __name__ == '__main__':
    print('Testing rover movement...')
    rover = RoverController()
    try:
        rover.forward(50)
        time.sleep(1)
        rover.backward(50)
        time.sleep(1)
        rover.spin_left(50)
        time.sleep(1)
        rover.spin_right(50)
        time.sleep(1)
        rover.stop()
        print('Rover test complete!')
    except KeyboardInterrupt:
        rover.stop()
    finally:
        rover.cleanup()
