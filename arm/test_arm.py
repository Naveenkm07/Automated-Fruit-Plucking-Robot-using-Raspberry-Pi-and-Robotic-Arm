import sys
import time

sys.path.insert(0, '/home/fruit/fruit_robot')
from arm.serial_comm import ArduinoComm

if __name__ == '__main__':
    arm = ArduinoComm()
    if not arm.connect():
        arm.find_arduino_port()
    
    if arm.is_connected:
        print('Testing arm...')
        arm.go_home()
        time.sleep(2)
        arm.open_gripper()
        time.sleep(1)
        arm.close_gripper()
        time.sleep(1)
        arm.pick()
        time.sleep(5)
        arm.go_home()
        print('Arm test complete!')
    else:
        print('Failed to connect to Arduino')
