import sys
import time

sys.path.insert(0, '/home/fruit/fruit_robot')
from rover.rover_movement import RoverController

if __name__ == '__main__':
    print('Manual control running. Use W/A/S/D to move.')
    rover = RoverController()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        rover.cleanup()
